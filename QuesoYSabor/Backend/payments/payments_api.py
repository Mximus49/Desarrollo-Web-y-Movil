from contextlib import asynccontextmanager
from datetime import datetime, timezone
import hashlib
import hmac
import json
import os
import secrets

import httpx
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Header, Depends, Request
from pydantic import BaseModel, Field, ValidationError
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

# Servicio de pagos. El navegador solo puede iniciar un pago; el resultado lo informa
# la pasarela con un aviso firmado (webhook) y este servicio es el que se lo comunica a orders.

DB_NAME = "quesoysabor_payments"
VAULT_ADDR = os.getenv("VAULT_ADDR", "https://127.0.0.1:8200").rstrip("/")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
ORDERS_URL = os.getenv("ORDERS_URL", "https://127.0.0.1:9002")

if not VAULT_TOKEN:
    raise RuntimeError("VAULT_TOKEN no esta configurado")

db = None
SECRETOS = {}


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
    global db
    SECRETOS["propia"] = leer_secreto_vault("quesoysabor/payments")["service_key"]
    SECRETOS["orders"] = leer_secreto_vault("quesoysabor/orders")["service_key"]
    SECRETOS["webhook"] = leer_secreto_vault("quesoysabor/pasarela")["webhook_secret"]
    client = AsyncIOMotorClient(leer_secreto_vault("quesoysabor/db/payments")["uri"])
    db = client[DB_NAME]
    # El indice unico es lo que impide procesar dos veces el mismo aviso de la pasarela
    await db.eventos_pasarela.create_index("evento_id", unique=True)
    yield
    client.close()


app = FastAPI(title="Payments Service", lifespan=lifespan)


def verificar_llamada(x_service_key: str = Header(default="")):
    if not secrets.compare_digest(x_service_key, SECRETOS["propia"]):
        raise HTTPException(status_code=403, detail="Llamada no autorizada")


def requiere_rol(*roles):
    def revisar(x_authenticated_roles: str = Header(default="")):
        if not set(x_authenticated_roles.split(",")) & set(roles):
            raise HTTPException(status_code=403, detail="Rol sin permiso")
    return revisar


class PagoIn(BaseModel):
    # Solo se acepta el pedido. Monto y estado los decide el servidor.
    order_id: str = Field(max_length=40)


class AvisoPasarela(BaseModel):
    evento_id: str = Field(min_length=8, max_length=80)
    payment_id: str = Field(max_length=40)
    estado: str = Field(pattern="^(APROBADO|RECHAZADO)$")
    monto: int


def pago_salida(doc) -> dict:
    return {
        "payment_id": str(doc["_id"]),
        "order_id": doc["order_id"],
        "monto": doc["monto"],
        "estado": doc["estado"],
        "creado": doc["creado"].isoformat()
    }


async def llamar_orders(metodo: str, ruta: str, json_body=None):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            return await client.request(metodo, f"{ORDERS_URL}{ruta}", json=json_body,
                                        headers={"X-Service-Key": SECRETOS["orders"]})
    except httpx.RequestError:
        raise HTTPException(503, "orders no disponible")


@app.get("/health", dependencies=[Depends(verificar_llamada)])
def health():
    return {"status": "OK", "service": "Payments"}


@app.post("/payments", status_code=201, dependencies=[Depends(verificar_llamada), Depends(requiere_rol("cliente"))])
async def iniciar_pago(pago: PagoIn, x_authenticated_user_id: str = Header()):
    resp = await llamar_orders("GET", f"/internal/orders/{pago.order_id}")
    if resp.status_code != 200:
        raise HTTPException(404, "Pedido no encontrado")
    pedido = resp.json()
    if pedido["user_id"] != x_authenticated_user_id:
        raise HTTPException(404, "Pedido no encontrado")
    if pedido["estado"] != "PENDIENTE_PAGO":
        raise HTTPException(409, "El pedido no esta pendiente de pago")
    # Si ya hay un pago pendiente para el pedido se reutiliza, asi no se cobra dos veces
    existente = await db.pagos.find_one({"order_id": pago.order_id, "estado": "PENDIENTE"})
    if existente:
        return pago_salida(existente)
    doc = {
        "order_id": pago.order_id,
        "user_id": x_authenticated_user_id,
        "monto": pedido["total"],
        "estado": "PENDIENTE",
        "creado": datetime.now(timezone.utc)
    }
    res = await db.pagos.insert_one(doc)
    doc["_id"] = res.inserted_id
    return pago_salida(doc)


@app.get("/payments/{payment_id}", dependencies=[Depends(verificar_llamada)])
async def consultar_pago(
    payment_id: str,
    x_authenticated_user_id: str = Header(default=""),
    x_authenticated_roles: str = Header(default="")
):
    doc = await db.pagos.find_one({"_id": ObjectId(payment_id)}) if ObjectId.is_valid(payment_id) else None
    es_admin = "admin" in x_authenticated_roles.split(",")
    if not doc or (not es_admin and doc["user_id"] != x_authenticated_user_id):
        raise HTTPException(404, "Pago no encontrado")
    return pago_salida(doc)


@app.post("/payments/webhook", dependencies=[Depends(verificar_llamada)])
async def aviso_pasarela(request: Request, x_firma: str = Header(default="")):
    # La firma se calcula sobre el cuerpo exacto que llego, con la clave que solo conocen
    # la pasarela y este servicio. Un cambio en cualquier dato invalida la firma.
    cuerpo = await request.body()
    esperada = hmac.new(SECRETOS["webhook"].encode(), cuerpo, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(x_firma, esperada):
        raise HTTPException(401, "Firma invalida")
    try:
        aviso = AvisoPasarela(**json.loads(cuerpo))
    except (ValueError, ValidationError):
        raise HTTPException(400, "Aviso con formato invalido")

    pago = await db.pagos.find_one({"_id": ObjectId(aviso.payment_id)}) if ObjectId.is_valid(aviso.payment_id) else None
    if not pago:
        raise HTTPException(404, "Pago no encontrado")
    if aviso.monto != pago["monto"]:
        raise HTTPException(400, "El monto informado no coincide con el pago")

    try:
        await db.eventos_pasarela.insert_one({"evento_id": aviso.evento_id, "recibido": datetime.now(timezone.utc)})
    except DuplicateKeyError:
        return {"duplicado": True, "estado": pago["estado"]}

    if pago["estado"] != "PENDIENTE":
        return {"duplicado": True, "estado": pago["estado"]}

    if aviso.estado == "APROBADO":
        resp = await llamar_orders("POST", f"/internal/orders/{pago['order_id']}/pagado",
                                   {"payment_id": str(pago["_id"]), "monto": pago["monto"]})
        if resp.status_code != 200:
            # Se borra el evento para que la pasarela pueda reintentar el aviso
            await db.eventos_pasarela.delete_one({"evento_id": aviso.evento_id})
            raise HTTPException(502, "orders no confirmo el pago, reintentar")

    await db.pagos.update_one({"_id": pago["_id"]}, {"$set": {"estado": aviso.estado, "evento_id": aviso.evento_id}})
    return {"duplicado": False, "estado": aviso.estado}
