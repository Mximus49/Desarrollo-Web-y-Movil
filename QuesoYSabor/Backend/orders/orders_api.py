from contextlib import asynccontextmanager
from datetime import date, datetime, time, timedelta, timezone
from html import escape
from typing import List, Optional
import asyncio
import json
import os
import secrets
import unicodedata

import httpx
import stomp
from bson import ObjectId
from fastapi import FastAPI, HTTPException, Header, Depends, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient

# Servicio de pedidos: crea pedidos, controla sus estados y emite la boleta.
# Los precios y el total siempre los calcula el servidor con los datos de inventory.
# Las ventas web se asocian a la caja WEB-01, operada por el cajero virtual (RF4, RF8).

DB_NAME = "quesoysabor_orders"
VAULT_ADDR = os.getenv("VAULT_ADDR", "https://127.0.0.1:8200").rstrip("/")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
INVENTORY_URL = os.getenv("INVENTORY_URL", "https://127.0.0.1:9001")
CLIENTS_URL = os.getenv("CLIENTS_URL", "https://127.0.0.1:9003")
STOMP_HOST = os.getenv("STOMP_HOST", "127.0.0.1")
STOMP_PORT = int(os.getenv("STOMP_PORT", "61613"))
# RabbitMQ usa el vhost "/", otros brokers pueden pedir otro valor
STOMP_VHOST = os.getenv("STOMP_VHOST", "/")
DESTINO = "/queue/pedidos"

COMUNAS_DESPACHO = ["providencia", "nunoa", "las condes", "santiago"]
LOCALES_RETIRO = ["Local Providencia", "Local Nunoa", "Local Las Condes"]
STAFF = {"admin", "despacho"}
CAJA_WEB = "WEB-01"
REINTENTO_AVISOS_SEG = 15

# Siguiente estado permitido segun la modalidad. Solo se prepara lo que ya esta pagado.
TRANSICIONES = {
    "DESPACHO": {"PAGADO": "EN_PREPARACION", "EN_PREPARACION": "EN_REPARTO", "EN_REPARTO": "ENTREGADO"},
    "RETIRO": {"PAGADO": "EN_PREPARACION", "EN_PREPARACION": "LISTO_RETIRO", "LISTO_RETIRO": "ENTREGADO"},
}

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
    SECRETOS["propia"] = leer_secreto_vault("quesoysabor/orders")["service_key"]
    SECRETOS["inventory"] = leer_secreto_vault("quesoysabor/inventory")["service_key"]
    SECRETOS["clients"] = leer_secreto_vault("quesoysabor/clients")["service_key"]
    SECRETOS["broker"] = leer_secreto_vault("quesoysabor/broker")
    client = AsyncIOMotorClient(leer_secreto_vault("quesoysabor/db/orders")["uri"])
    db = client[DB_NAME]
    await db.pedidos.create_index("user_id")
    tarea = asyncio.create_task(reenviar_avisos_pendientes())
    yield
    tarea.cancel()
    client.close()


app = FastAPI(title="Orders Service", lifespan=lifespan)


def verificar_llamada(x_service_key: str = Header(default="")):
    if not secrets.compare_digest(x_service_key, SECRETOS["propia"]):
        raise HTTPException(status_code=403, detail="Llamada no autorizada")


def requiere_rol(*roles):
    def revisar(x_authenticated_roles: str = Header(default="")):
        if not set(x_authenticated_roles.split(",")) & set(roles):
            raise HTTPException(status_code=403, detail="Rol sin permiso")
    return revisar


class LineaPedido(BaseModel):
    product_id: str = Field(max_length=64)
    cantidad: int = Field(gt=0, le=20)


class PedidoIn(BaseModel):
    # Si el navegador manda precio, total o estado, pydantic los ignora
    items: List[LineaPedido] = Field(min_length=1, max_length=30)
    modalidad: str = Field(pattern="^(DESPACHO|RETIRO)$")
    local_retiro: Optional[str] = None


class AnularIn(BaseModel):
    motivo: str = Field(min_length=5, max_length=300)


class EstadoIn(BaseModel):
    estado: str = Field(max_length=30)


class PagoConfirmado(BaseModel):
    payment_id: str
    monto: int


def pedido_salida(doc, mostrar_cliente: bool = False) -> dict:
    datos = {
        "id": str(doc["_id"]),
        "estado": doc["estado"],
        "modalidad": doc["modalidad"],
        "items": doc["items"],
        "total": doc["total"],
        "creado": doc["creado"].isoformat(),
        "boleta": doc.get("boleta"),
        "motivo_anulacion": doc.get("motivo_anulacion"),
        "local_retiro": doc.get("local_retiro"),
        "direccion_entrega": doc.get("direccion_entrega"),
    }
    if mostrar_cliente:
        datos["user_id"] = doc["user_id"]
        datos["cliente"] = doc.get("cliente")
    return datos


def sin_tildes(texto: str) -> str:
    # Asi "Ñuñoa" y "nunoa" se consideran la misma comuna
    texto = unicodedata.normalize("NFKD", texto.lower().strip())
    return "".join(c for c in texto if not unicodedata.combining(c))


def es_staff(roles: str) -> bool:
    return bool(set(roles.split(",")) & STAFF)


def enviar_stomp(eventos: list) -> bool:
    try:
        conexion = stomp.Connection12([(STOMP_HOST, STOMP_PORT)], vhost=STOMP_VHOST, reconnect_attempts_max=1)
        conexion.connect(SECRETOS["broker"]["usuario"], SECRETOS["broker"]["clave"], wait=True)
        for evento in eventos:
            conexion.send(
                destination=DESTINO,
                body=json.dumps(evento),
                headers={"content-type": "application/json", "x-formato": "json", "persistent": "true"}
            )
        conexion.disconnect()
        return True
    except Exception as exc:
        print(f"Aviso no enviado al broker STOMP: {type(exc).__name__}")
        return False


async def publicar_evento(evento: dict):
    # Aviso a la cola de notificaciones. Si el broker no esta, el pedido sigue igual y el aviso
    # queda guardado en avisos_pendientes para reenviarlo cuando el broker vuelva.
    if not await asyncio.to_thread(enviar_stomp, [evento]):
        await db.avisos_pendientes.insert_one({"evento": evento, "creado": datetime.now(timezone.utc)})


async def reenviar_avisos_pendientes():
    while True:
        await asyncio.sleep(REINTENTO_AVISOS_SEG)
        try:
            pendientes = await db.avisos_pendientes.find().sort("creado", 1).to_list(100)
            if pendientes and await asyncio.to_thread(enviar_stomp, [p["evento"] for p in pendientes]):
                await db.avisos_pendientes.delete_many({"_id": {"$in": [p["_id"] for p in pendientes]}})
                print(f"Avisos pendientes reenviados: {len(pendientes)}")
        except Exception as exc:
            print(f"Error al reenviar avisos pendientes: {type(exc).__name__}")


def datos_boleta(doc) -> dict:
    # Lo necesario para armar el correo de la boleta, sin datos personales
    return {"tipo": "pedido_pagado", "order_id": str(doc["_id"]), "user_id": doc["user_id"],
            "folio": doc["boleta"]["folio"], "boleta": doc["boleta"],
            "items": [{"nombre": i["nombre"], "cantidad": i["cantidad"], "subtotal": i["subtotal"]} for i in doc["items"]]}


async def llamar_servicio(url: str, clave: str, metodo: str = "GET", json_body=None):
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            return await client.request(metodo, url, json=json_body, headers={"X-Service-Key": clave})
    except httpx.RequestError:
        raise HTTPException(503, "Servicio interno no disponible, intente mas tarde")


async def buscar_pedido(order_id: str):
    if not ObjectId.is_valid(order_id):
        raise HTTPException(404, "Pedido no encontrado")
    doc = await db.pedidos.find_one({"_id": ObjectId(order_id)})
    if not doc:
        raise HTTPException(404, "Pedido no encontrado")
    return doc


@app.get("/health", dependencies=[Depends(verificar_llamada)])
def health():
    return {"status": "OK", "service": "Orders"}


@app.post("/orders", status_code=201, dependencies=[Depends(verificar_llamada), Depends(requiere_rol("cliente"))])
async def crear_pedido(pedido: PedidoIn, x_authenticated_user_id: str = Header()):
    datos_entrega = {}
    if pedido.modalidad == "DESPACHO":
        resp = await llamar_servicio(f"{CLIENTS_URL}/internal/clients/{x_authenticated_user_id}", SECRETOS["clients"])
        perfil = resp.json() if resp.status_code == 200 else {}
        if not perfil.get("direccion") or not perfil.get("comuna"):
            raise HTTPException(400, "Complete su direccion y comuna en el perfil antes de pedir despacho")
        if sin_tildes(perfil["comuna"]) not in COMUNAS_DESPACHO:
            raise HTTPException(400, "La comuna esta fuera del radio de despacho")
        datos_entrega = {
            "direccion_entrega": f'{perfil["direccion"]}, {perfil["comuna"]}',
            "cliente": {"nombre": perfil.get("nombre"), "telefono": perfil.get("telefono")}
        }
    elif pedido.local_retiro not in LOCALES_RETIRO:
        raise HTTPException(400, f"Local de retiro invalido, opciones: {LOCALES_RETIRO}")

    # inventory descuenta el stock y devuelve los precios oficiales
    resp = await llamar_servicio(
        f"{INVENTORY_URL}/internal/reservar", SECRETOS["inventory"], "POST",
        {"items": [linea.model_dump() for linea in pedido.items]}
    )
    if resp.status_code != 200:
        raise HTTPException(resp.status_code, resp.json().get("detail", "No se pudo reservar stock"))
    items = resp.json()["items"]
    for item in items:
        item["subtotal"] = item["precio_unitario"] * item["cantidad"]

    doc = {
        "user_id": x_authenticated_user_id,
        "estado": "PENDIENTE_PAGO",
        "modalidad": pedido.modalidad,
        "local_retiro": pedido.local_retiro if pedido.modalidad == "RETIRO" else None,
        "items": items,
        "total": sum(item["subtotal"] for item in items),
        "creado": datetime.now(timezone.utc),
        **datos_entrega
    }
    res = await db.pedidos.insert_one(doc)
    doc["_id"] = res.inserted_id
    return pedido_salida(doc)


@app.get("/orders/mine", dependencies=[Depends(verificar_llamada), Depends(requiere_rol("cliente"))])
async def mis_pedidos(
    x_authenticated_user_id: str = Header(),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    cursor = db.pedidos.find({"user_id": x_authenticated_user_id}).sort("creado", -1).skip(skip).limit(limit)
    return [pedido_salida(doc) async for doc in cursor]


@app.get("/orders/{order_id}", dependencies=[Depends(verificar_llamada)])
async def obtener_pedido(
    order_id: str,
    x_authenticated_user_id: str = Header(default=""),
    x_authenticated_roles: str = Header(default="")
):
    doc = await buscar_pedido(order_id)
    staff = es_staff(x_authenticated_roles)
    # Si el pedido es de otro cliente respondemos 404 para no revelar que existe
    if not staff and doc["user_id"] != x_authenticated_user_id:
        raise HTTPException(404, "Pedido no encontrado")
    return pedido_salida(doc, mostrar_cliente=staff)


@app.post("/orders/{order_id}/cancel", dependencies=[Depends(verificar_llamada), Depends(requiere_rol("cliente", "admin"))])
async def anular_pedido(
    order_id: str,
    anular: AnularIn,
    x_authenticated_user_id: str = Header(),
    x_authenticated_roles: str = Header()
):
    doc = await buscar_pedido(order_id)
    es_admin = "admin" in x_authenticated_roles.split(",")
    if not es_admin and doc["user_id"] != x_authenticated_user_id:
        raise HTTPException(404, "Pedido no encontrado")
    if doc["estado"] not in ("PENDIENTE_PAGO", "PAGADO"):
        raise HTTPException(409, f"No se puede anular un pedido en estado {doc['estado']}")

    lineas = [{"product_id": i["product_id"], "cantidad": i["cantidad"]} for i in doc["items"]]
    resp = await llamar_servicio(f"{INVENTORY_URL}/internal/liberar", SECRETOS["inventory"], "POST", {"items": lineas})
    if resp.status_code != 200:
        raise HTTPException(503, "No se pudo devolver el stock, el pedido no se anulo")

    # No se borra el pedido: queda en el historial con su motivo
    cambios = {"estado": "ANULADO", "motivo_anulacion": anular.motivo}
    if doc["estado"] == "PAGADO":
        cambios["reembolso_pendiente"] = True
    # El filtro por estado evita anular dos veces si llegan dos solicitudes juntas
    res = await db.pedidos.update_one({"_id": doc["_id"], "estado": doc["estado"]}, {"$set": cambios})
    if res.modified_count == 0:
        raise HTTPException(409, "El pedido cambio de estado, intente de nuevo")
    await publicar_evento({"tipo": "pedido_anulado", "order_id": order_id, "user_id": doc["user_id"]})
    return pedido_salida(await buscar_pedido(order_id))


@app.get("/admin/orders", dependencies=[Depends(verificar_llamada), Depends(requiere_rol("admin", "despacho"))])
async def listar_pedidos(
    estado: Optional[str] = Query(None, max_length=30),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200)
):
    query = {"estado": estado} if estado else {}
    # Orden de llegada: el pedido mas antiguo primero, como pide el caso para despacho
    cursor = db.pedidos.find(query).sort("creado", 1).skip(skip).limit(limit)
    return [pedido_salida(doc, mostrar_cliente=True) async for doc in cursor]


@app.patch("/admin/orders/{order_id}/estado", dependencies=[Depends(verificar_llamada), Depends(requiere_rol("admin", "despacho"))])
async def cambiar_estado(order_id: str, cambio: EstadoIn):
    doc = await buscar_pedido(order_id)
    siguiente = TRANSICIONES[doc["modalidad"]].get(doc["estado"])
    if cambio.estado != siguiente:
        raise HTTPException(409, f"Desde {doc['estado']} solo se puede pasar a {siguiente}")
    await db.pedidos.update_one({"_id": doc["_id"], "estado": doc["estado"]}, {"$set": {"estado": siguiente}})
    await publicar_evento({"tipo": "cambio_estado", "order_id": order_id, "user_id": doc["user_id"], "estado": siguiente})
    return pedido_salida(await buscar_pedido(order_id), mostrar_cliente=True)


@app.get("/admin/orders/imprimir", response_class=HTMLResponse,
         dependencies=[Depends(verificar_llamada), Depends(requiere_rol("admin", "despacho"))])
async def imprimir_ordenes(estado: str = Query("PAGADO", pattern="^(PAGADO|EN_PREPARACION)$")):
    # RF13: ordenes de despacho listas para imprimir y entregar a cocina, en orden de llegada
    pedidos = await db.pedidos.find({"estado": estado}).sort("creado", 1).to_list(200)
    bloques = []
    for n, doc in enumerate(pedidos, start=1):
        cliente = doc.get("cliente") or {}
        destino = (f"Despacho a: {escape(doc.get('direccion_entrega') or '')}" if doc["modalidad"] == "DESPACHO"
                   else f"Retiro en: {escape(doc.get('local_retiro') or '')}")
        filas = "".join(f"<tr><td>{i['cantidad']}</td><td>{escape(i['nombre'])}</td></tr>" for i in doc["items"])
        folio = (doc.get("boleta") or {}).get("folio", "-")
        bloques.append(
            f"<section class='orden'><h2>{n}. Pedido {doc['_id']}</h2>"
            f"<p>Recibido: {doc['creado']:%Y-%m-%d %H:%M} UTC | Boleta: {folio}</p>"
            f"<p>{destino}<br>Cliente: {escape(cliente.get('nombre') or '-')} | Telefono: {escape(cliente.get('telefono') or '-')}</p>"
            f"<table><tr><th>Cant.</th><th>Producto</th></tr>{filas}</table></section>")
    return ("<!doctype html><html lang='es'><head><meta charset='utf-8'><title>Ordenes de despacho</title>"
            "<style>body{font-family:sans-serif;margin:16px}.orden{border:1px solid #000;padding:8px;margin:8px 0;"
            "page-break-inside:avoid}table{border-collapse:collapse}td,th{border:1px solid #999;padding:2px 8px}</style>"
            f"</head><body><h1>Ordenes de despacho ({escape(estado)})</h1>"
            f"<p>Generado: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC | {len(pedidos)} pedidos en orden de llegada</p>"
            + ("".join(bloques) or "<p>No hay pedidos pendientes.</p>") + "</body></html>")


@app.get("/admin/caja", dependencies=[Depends(verificar_llamada), Depends(requiere_rol("admin", "cajero", "dueno"))])
async def caja_del_dia(fecha: Optional[date] = None):
    # Ventas de la caja web en un dia (UTC): lo que el dueno consulta antes de retirar lo recaudado
    dia = fecha or datetime.now(timezone.utc).date()
    inicio = datetime.combine(dia, time.min, tzinfo=timezone.utc)
    filtro = {"boleta": {"$ne": None}, "pagado": {"$gte": inicio, "$lt": inicio + timedelta(days=1)}}
    ventas = [{"folio": d["boleta"]["folio"], "order_id": str(d["_id"]), "total": d["total"],
               "hora": d["pagado"].strftime("%H:%M"), "estado": d["estado"]}
              async for d in db.pedidos.find(filtro).sort("pagado", 1)]
    validas = [v for v in ventas if v["estado"] != "ANULADO"]
    return {"caja": CAJA_WEB, "operada_por": "cajero virtual", "fecha": dia.isoformat(), "ventas": ventas,
            "cantidad": len(validas), "total_recaudado": sum(v["total"] for v in validas),
            "reembolsos_pendientes": sum(v["total"] for v in ventas if v["estado"] == "ANULADO")}


@app.post("/admin/orders/{order_id}/boleta", dependencies=[Depends(verificar_llamada), Depends(requiere_rol("admin", "cajero"))])
async def reenviar_boleta(order_id: str):
    # El cajero virtual vuelve a enviar la boleta al correo del cliente
    doc = await buscar_pedido(order_id)
    if not doc.get("boleta"):
        raise HTTPException(409, "El pedido no tiene boleta emitida")
    await publicar_evento(datos_boleta(doc))
    return {"order_id": order_id, "folio": doc["boleta"]["folio"], "reenviada": True}


# Rutas internas usadas por payments y analytics. El gateway no las publica.

@app.get("/internal/orders/{order_id}", dependencies=[Depends(verificar_llamada)])
async def pedido_interno(order_id: str):
    doc = await buscar_pedido(order_id)
    return {"id": order_id, "user_id": doc["user_id"], "estado": doc["estado"], "total": doc["total"]}


@app.post("/internal/orders/{order_id}/pagado", dependencies=[Depends(verificar_llamada)])
async def marcar_pagado(order_id: str, pago: PagoConfirmado):
    doc = await buscar_pedido(order_id)
    if doc["estado"] == "PAGADO" and doc.get("payment_id") == pago.payment_id:
        return pedido_salida(doc)
    if doc["estado"] != "PENDIENTE_PAGO":
        raise HTTPException(409, "El pedido no esta pendiente de pago")
    if pago.monto != doc["total"]:
        raise HTTPException(400, "El monto pagado no coincide con el total del pedido")
    # Boleta electronica: folio correlativo e IVA incluido en el total
    contador = await db.contadores.find_one_and_update(
        {"_id": "boleta"}, {"$inc": {"valor": 1}}, upsert=True, return_document=True
    )
    neto = round(doc["total"] / 1.19)
    boleta = {"folio": contador["valor"], "neto": neto, "iva": doc["total"] - neto, "total": doc["total"],
              "fecha": datetime.now(timezone.utc).isoformat(), "caja": CAJA_WEB, "emitida_por": "cajero virtual"}
    await db.pedidos.update_one(
        {"_id": doc["_id"], "estado": "PENDIENTE_PAGO"},
        {"$set": {"estado": "PAGADO", "payment_id": pago.payment_id, "pagado": datetime.now(timezone.utc), "boleta": boleta}}
    )
    pagado = await buscar_pedido(order_id)
    await publicar_evento(datos_boleta(pagado))
    return pedido_salida(pagado)


@app.get("/internal/ventas", dependencies=[Depends(verificar_llamada)])
async def ventas_internas():
    # Solo lo necesario para reportes, sin datos del cliente
    estados = ["PAGADO", "EN_PREPARACION", "EN_REPARTO", "LISTO_RETIRO", "ENTREGADO"]
    ventas = []
    async for doc in db.pedidos.find({"estado": {"$in": estados}}):
        ventas.append({
            "fecha": doc.get("pagado", doc["creado"]).date().isoformat(),
            "total": doc["total"],
            "items": [{"product_id": i["product_id"], "nombre": i["nombre"], "cantidad": i["cantidad"], "subtotal": i["subtotal"]} for i in doc["items"]]
        })
    return ventas
