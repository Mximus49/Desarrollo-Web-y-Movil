from datetime import datetime, timedelta, timezone
from contextlib import asynccontextmanager
import hashlib
import os
import re
import secrets
from typing import List

import httpx
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId

# Servicio de autenticacion de Queso & Sabor.
# Usuarios y sesiones guardados en MongoDB, contrasenas como hash PBKDF2 con sal (nunca en texto plano).
# Antes de crear una cuenta comprueba con el proveedor de mensajeria que el correo exista (RF11).

DB_NAME = "quesoysabor_auth"
VAULT_ADDR = os.getenv("VAULT_ADDR", "https://127.0.0.1:8200").rstrip("/")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
MENSAJERIA_URL = os.getenv("MENSAJERIA_URL", "https://127.0.0.1:8300")
ROLES_PERSONAL = {"admin", "despacho", "dueno", "cajero"}

TOKEN_LIFETIME_MINUTES = 30
ITERACIONES = 200_000

if not VAULT_TOKEN:
    raise RuntimeError("VAULT_TOKEN no esta configurado")

db = None
SERVICE_KEY = None
MENSAJERIA_KEY = None


def leer_secreto_vault(ruta: str) -> dict:
    # Lee un secreto KV v2 de Vault. Si Vault no responde el servicio no parte.
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
    global db, SERVICE_KEY, MENSAJERIA_KEY
    SERVICE_KEY = leer_secreto_vault("quesoysabor/auth")["service_key"]
    MENSAJERIA_KEY = leer_secreto_vault("quesoysabor/mensajeria")["api_key"]
    # Usuario de MongoDB propio de auth, con permiso solo sobre quesoysabor_auth
    client = AsyncIOMotorClient(leer_secreto_vault("quesoysabor/db/auth")["uri"])
    db = client[DB_NAME]
    await db.usuarios.create_index("email", unique=True)
    # MongoDB borra solo las sesiones vencidas gracias a este indice TTL
    await db.sesiones.create_index("expires_at", expireAfterSeconds=0)
    yield
    client.close()


app = FastAPI(
    title="Authentication Service",
    description="Login, registro y validacion de tokens de Queso & Sabor",
    lifespan=lifespan
)


def hash_password(password: str, sal: bytes | None = None) -> str:
    sal = sal or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), sal, ITERACIONES)
    return f"pbkdf2${ITERACIONES}${sal.hex()}${digest.hex()}"


def password_correcta(password: str, guardado: str) -> bool:
    _, iteraciones, sal, digest = guardado.split("$")
    calculado = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(sal), int(iteraciones))
    return secrets.compare_digest(calculado.hex(), digest)


def hash_token(token: str) -> str:
    # En la base se guarda el hash del token, asi una copia de la base no sirve para entrar
    return hashlib.sha256(token.encode()).hexdigest()


def verificar_llamada(x_service_key: str = Header(default="")):
    if not secrets.compare_digest(x_service_key, SERVICE_KEY):
        raise HTTPException(status_code=403, detail="Llamada no autorizada")


def solo_admin(x_authenticated_roles: str = Header(default="")):
    if "admin" not in x_authenticated_roles.split(","):
        raise HTTPException(status_code=403, detail="Rol sin permiso")


def politica_password(password: str):
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise HTTPException(status_code=422, detail="La contrasena debe tener letras y numeros")


async def verificar_correo(email: str):
    # RF11: el correo debe existir y estar activo segun la API de mensajeria
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.post(f"{MENSAJERIA_URL}/v1/verificar", json={"email": email},
                                  headers={"Authorization": f"Bearer {MENSAJERIA_KEY}"})
    except httpx.RequestError:
        raise HTTPException(status_code=503, detail="No se pudo validar el correo, intente mas tarde")
    if r.status_code != 200:
        raise HTTPException(status_code=503, detail="No se pudo validar el correo, intente mas tarde")
    if not r.json().get("activo"):
        raise HTTPException(status_code=422, detail="El correo no existe o no esta activo")


class LoginRequest(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=1, max_length=128)


class RegisterRequest(BaseModel):
    email: str = Field(max_length=254, pattern=r"^[^@\s]+@[^@\s]+\.[a-zA-Z]{2,}$")
    nombre: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=8, max_length=128)


class UsuarioPersonal(RegisterRequest):
    roles: List[str] = Field(min_length=1, max_length=3)


class TokenRequest(BaseModel):
    token: str = Field(max_length=200)


@app.post("/register", status_code=201, dependencies=[Depends(verificar_llamada)])
async def register(request: RegisterRequest):
    politica_password(request.password)
    email = request.email.lower()
    if await db.usuarios.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="El correo ya esta registrado")
    await verificar_correo(email)
    # Por esta ruta solo se crean clientes (desde la web o por el admin en el local).
    # El personal se crea en /admin/users.
    res = await db.usuarios.insert_one({
        "email": email,
        "nombre": request.nombre,
        "password_hash": hash_password(request.password),
        "roles": ["cliente"],
        "activo": True,
        "email_verificado": True
    })
    return {"user_id": str(res.inserted_id), "email": email, "roles": ["cliente"]}


@app.post("/login", dependencies=[Depends(verificar_llamada)])
async def login(request: LoginRequest):
    user = await db.usuarios.find_one({"email": request.email.lower()})
    # Mismo mensaje si el correo no existe o la clave es mala, para no revelar cuentas
    if user is None or not password_correcta(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    if not user.get("activo", True):
        raise HTTPException(status_code=403, detail="Usuario desactivado")
    access_token = secrets.token_urlsafe(32)
    expiration = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_LIFETIME_MINUTES)
    await db.sesiones.insert_one({
        "token_hash": hash_token(access_token),
        "user_id": str(user["_id"]),
        "expires_at": expiration
    })
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": TOKEN_LIFETIME_MINUTES * 60
    }


@app.post("/introspect", dependencies=[Depends(verificar_llamada)])
async def introspect(request: TokenRequest):
    session = await db.sesiones.find_one({"token_hash": hash_token(request.token)})
    if session is None:
        return {"active": False}
    expires_at = session["expires_at"].replace(tzinfo=timezone.utc)
    if datetime.now(timezone.utc) > expires_at:
        await db.sesiones.delete_one({"_id": session["_id"]})
        return {"active": False}

    user = await db.usuarios.find_one({"_id": ObjectId(session["user_id"])})
    if user is None or not user.get("activo", True):
        return {"active": False}
    return {
        "active": True,
        "user_id": session["user_id"],
        "email": user["email"],
        "nombre": user["nombre"],
        "roles": user["roles"],
        "expires_at": expires_at.isoformat()
    }


@app.post("/logout", dependencies=[Depends(verificar_llamada)])
async def logout(request: TokenRequest):
    await db.sesiones.delete_one({"token_hash": hash_token(request.token)})
    return {"message": "Sesion finalizada"}


@app.get("/health", dependencies=[Depends(verificar_llamada)])
async def health():
    return {"status": "OK", "service": "Authentication service"}


# Mantenedor de usuarios del personal (solo admin)

@app.get("/admin/users", dependencies=[Depends(verificar_llamada), Depends(solo_admin)])
async def listar_usuarios():
    usuarios = []
    async for u in db.usuarios.find({}, {"password_hash": 0}).sort("email"):
        usuarios.append({"user_id": str(u["_id"]), "email": u["email"], "nombre": u["nombre"],
                         "roles": u["roles"], "activo": u.get("activo", True)})
    return usuarios


@app.post("/admin/users", status_code=201, dependencies=[Depends(verificar_llamada), Depends(solo_admin)])
async def crear_usuario_personal(request: UsuarioPersonal):
    if not set(request.roles) <= ROLES_PERSONAL:
        raise HTTPException(status_code=422, detail="Roles permitidos: admin, despacho, dueno, cajero")
    politica_password(request.password)
    email = request.email.lower()
    if await db.usuarios.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="El correo ya esta registrado")
    await verificar_correo(email)
    res = await db.usuarios.insert_one({
        "email": email, "nombre": request.nombre, "password_hash": hash_password(request.password),
        "roles": request.roles, "activo": True, "email_verificado": True
    })
    return {"user_id": str(res.inserted_id), "email": email, "roles": request.roles}


@app.delete("/admin/users/{user_id}", dependencies=[Depends(verificar_llamada), Depends(solo_admin)])
async def desactivar_usuario(user_id: str, x_authenticated_user_id: str = Header()):
    # No se borra para conservar el historial; se desactiva y se cierran sus sesiones
    if user_id == x_authenticated_user_id:
        raise HTTPException(status_code=400, detail="No puede desactivar su propia cuenta")
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    res = await db.usuarios.update_one({"_id": ObjectId(user_id)}, {"$set": {"activo": False}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    await db.sesiones.delete_many({"user_id": user_id})
    return {"user_id": user_id, "activo": False}


# Ruta interna: notifications la usa para obtener el correo del destinatario al enviar un aviso.
# El correo no viaja en la cola de mensajes, se consulta aqui solo al momento de enviar.

@app.get("/internal/users/{user_id}", dependencies=[Depends(verificar_llamada)])
async def usuario_interno(user_id: str):
    user = await db.usuarios.find_one({"_id": ObjectId(user_id)}) if ObjectId.is_valid(user_id) else None
    if user is None or not user.get("activo", True):
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"email": user["email"], "nombre": user["nombre"]}
