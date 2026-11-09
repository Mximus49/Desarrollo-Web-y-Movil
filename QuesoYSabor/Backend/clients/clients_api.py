from contextlib import asynccontextmanager
from datetime import date
from typing import Literal, Optional
import os
import secrets

import httpx
from fastapi import FastAPI, HTTPException, Header, Depends, Query
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient

# Servicio de clientes: perfil con RUT, telefono y direccion de despacho.
# Son datos personales, por eso cada cliente solo ve el suyo y el admin ve el RUT enmascarado.
# El admin tambien puede registrar clientes en el local (RF6); la cuenta la crea auth.

DB_NAME = "quesoysabor_clients"
VAULT_ADDR = os.getenv("VAULT_ADDR", "https://127.0.0.1:8200").rstrip("/")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
AUTH_URL = os.getenv("AUTH_SERVICE_URL", "https://127.0.0.1:8100")

if not VAULT_TOKEN:
    raise RuntimeError("VAULT_TOKEN no esta configurado")

coll = None
SERVICE_KEY = None
AUTH_KEY = None


def leer_secreto_vault(ruta: str) -> dict:
    response = httpx.get(
        f"{VAULT_ADDR}/v1/secret/data/{ruta}",
        headers={"X-Vault-Token": VAULT_TOKEN},
        timeout=5.0
    )
    if response.status_code != 200:
        raise RuntimeError(f"No fue posible leer {ruta} desde Vault")
    return response.json()["data"]["data"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global coll, SERVICE_KEY, AUTH_KEY
    SERVICE_KEY = leer_secreto_vault("quesoysabor/clients")["service_key"]
    AUTH_KEY = leer_secreto_vault("quesoysabor/auth")["service_key"]
    client = AsyncIOMotorClient(leer_secreto_vault("quesoysabor/db/clients")["uri"])
    coll = client[DB_NAME]["clientes"]
    await coll.create_index("rut", unique=True, sparse=True)
    yield
    client.close()


app = FastAPI(title="Clients Service", lifespan=lifespan)


def verificar_llamada(x_service_key: str = Header(default="")):
    if not secrets.compare_digest(x_service_key, SERVICE_KEY):
        raise HTTPException(status_code=403, detail="Llamada no autorizada")


def requiere_rol(*roles):
    def revisar(x_authenticated_roles: str = Header(default="")):
        if not set(x_authenticated_roles.split(",")) & set(roles):
            raise HTTPException(status_code=403, detail="Rol sin permiso")
    return revisar


def rut_valido(rut: str) -> bool:
    # Calcula el digito verificador con modulo 11
    cuerpo, dv = rut[:-2], rut[-1].upper()
    suma, factor = 0, 2
    for digito in reversed(cuerpo):
        suma += int(digito) * factor
        factor = 2 if factor == 7 else factor + 1
    esperado = 11 - suma % 11
    esperado = "0" if esperado == 11 else "K" if esperado == 10 else str(esperado)
    return dv == esperado


class PerfilIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=80)
    rut: Optional[str] = Field(default=None, pattern=r"^\d{7,8}-[\dkK]$", description="Sin puntos, ej 12345678-5")
    telefono: Optional[str] = Field(default=None, pattern=r"^\+569\d{8}$")
    direccion: Optional[str] = Field(default=None, min_length=5, max_length=200)
    comuna: Optional[str] = Field(default=None, max_length=60)
    provincia: Optional[str] = Field(default=None, max_length=60)
    region: Optional[str] = Field(default=None, max_length=60)
    fecha_nacimiento: Optional[date] = None
    sexo: Optional[Literal["F", "M", "Otro", "No informa"]] = None


class ClienteNuevo(PerfilIn):
    # Registro presencial: el admin ingresa los datos con el cliente y este elige su contrasena
    email: str = Field(max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
    password: str = Field(min_length=8, max_length=128)


def validar_perfil(perfil: PerfilIn):
    if perfil.rut and not rut_valido(perfil.rut):
        raise HTTPException(422, "RUT invalido")
    if perfil.fecha_nacimiento and not date(1900, 1, 1) <= perfil.fecha_nacimiento < date.today():
        raise HTTPException(422, "Fecha de nacimiento invalida")


def datos_perfil(perfil: PerfilIn) -> dict:
    datos = perfil.model_dump(include=set(PerfilIn.model_fields))
    if datos["fecha_nacimiento"]:
        datos["fecha_nacimiento"] = datos["fecha_nacimiento"].isoformat()
    if perfil.rut:
        datos["rut"] = perfil.rut.upper()
    else:
        datos.pop("rut")
    return datos


async def rut_de_otro(rut: Optional[str], user_id: str) -> bool:
    return bool(rut) and await coll.find_one({"rut": rut.upper(), "_id": {"$ne": user_id}}) is not None


def perfil_salida(doc) -> dict:
    return {
        "user_id": doc["_id"],
        "email": doc.get("email"),
        "nombre": doc.get("nombre"),
        "rut": doc.get("rut"),
        "telefono": doc.get("telefono"),
        "direccion": doc.get("direccion"),
        "comuna": doc.get("comuna"),
        "provincia": doc.get("provincia"),
        "region": doc.get("region"),
        "fecha_nacimiento": doc.get("fecha_nacimiento"),
        "sexo": doc.get("sexo"),
        "perfil_completo": bool(doc.get("direccion") and doc.get("comuna") and doc.get("telefono"))
    }


def enmascarar_rut(rut: Optional[str]) -> Optional[str]:
    if not rut:
        return None
    return "*" * (len(rut) - 5) + rut[-5:]


@app.get("/health", dependencies=[Depends(verificar_llamada)])
def health():
    return {"status": "OK", "service": "Clients"}


@app.get("/clients/me", dependencies=[Depends(verificar_llamada), Depends(requiere_rol("cliente"))])
async def mi_perfil(
    x_authenticated_user_id: str = Header(),
    x_authenticated_user: str = Header(default="")
):
    # El user_id sale de la sesion verificada por el gateway, nunca de la URL
    doc = await coll.find_one({"_id": x_authenticated_user_id})
    if not doc:
        return perfil_salida({"_id": x_authenticated_user_id, "email": x_authenticated_user})
    return perfil_salida(doc)


@app.put("/clients/me", dependencies=[Depends(verificar_llamada), Depends(requiere_rol("cliente"))])
async def actualizar_perfil(
    perfil: PerfilIn,
    x_authenticated_user_id: str = Header(),
    x_authenticated_user: str = Header(default="")
):
    validar_perfil(perfil)
    if await rut_de_otro(perfil.rut, x_authenticated_user_id):
        raise HTTPException(409, "El RUT ya esta registrado por otro cliente")
    datos = datos_perfil(perfil)
    datos["email"] = x_authenticated_user
    await coll.update_one({"_id": x_authenticated_user_id}, {"$set": datos}, upsert=True)
    return perfil_salida(await coll.find_one({"_id": x_authenticated_user_id}))


@app.get("/admin/clients", dependencies=[Depends(verificar_llamada), Depends(requiere_rol("admin"))])
async def listar_clientes(skip: int = Query(0, ge=0), limit: int = Query(50, ge=1, le=200)):
    clientes = []
    async for doc in coll.find().skip(skip).limit(limit):
        clientes.append({
            "user_id": doc["_id"],
            "nombre": doc.get("nombre"),
            "email": doc.get("email"),
            "rut": enmascarar_rut(doc.get("rut")),
            "comuna": doc.get("comuna")
        })
    return clientes


@app.post("/admin/clients", status_code=201, dependencies=[Depends(verificar_llamada), Depends(requiere_rol("admin"))])
async def registrar_cliente(nuevo: ClienteNuevo):
    # RF6: registro en el local. auth crea la cuenta (y valida el correo, RF11); aqui se guarda el perfil.
    validar_perfil(nuevo)
    if await rut_de_otro(nuevo.rut, ""):
        raise HTTPException(409, "El RUT ya esta registrado por otro cliente")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(f"{AUTH_URL}/register", headers={"X-Service-Key": AUTH_KEY},
                                  json={"email": nuevo.email, "nombre": nuevo.nombre, "password": nuevo.password})
    except httpx.RequestError:
        raise HTTPException(503, "Servicio de autenticacion no disponible")
    if r.status_code != 201:
        raise HTTPException(r.status_code, r.json().get("detail", "No se pudo crear la cuenta"))
    cuenta = r.json()
    datos = datos_perfil(nuevo)
    datos["email"] = cuenta["email"]
    await coll.update_one({"_id": cuenta["user_id"]}, {"$set": datos}, upsert=True)
    return perfil_salida(await coll.find_one({"_id": cuenta["user_id"]}))


# Ruta interna: orders la usa para copiar la direccion de despacho al crear un pedido.

@app.get("/internal/clients/{user_id}", dependencies=[Depends(verificar_llamada)])
async def cliente_interno(user_id: str):
    doc = await coll.find_one({"_id": user_id})
    if not doc:
        raise HTTPException(404, "Cliente sin perfil")
    return {
        "nombre": doc.get("nombre"),
        "direccion": doc.get("direccion"),
        "comuna": doc.get("comuna"),
        "telefono": doc.get("telefono")
    }
