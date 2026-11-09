from contextlib import asynccontextmanager
from typing import List, Optional
import os
import secrets

import httpx
from fastapi import FastAPI, HTTPException, Header, Depends, Query
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient

# Servicio de inventario: catalogo, ofertas y stock.
# Es el unico que puede cambiar el stock y el precio de los productos.

DB_NAME = "quesoysabor_inventory"
VAULT_ADDR = os.getenv("VAULT_ADDR", "https://127.0.0.1:8200").rstrip("/")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")

CATEGORIAS = ["madurado", "fresco", "especial"]

if not VAULT_TOKEN:
    raise RuntimeError("VAULT_TOKEN no esta configurado")

coll = None
SERVICE_KEY = None


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
    global coll, SERVICE_KEY
    SERVICE_KEY = leer_secreto_vault("quesoysabor/inventory")["service_key"]
    # Usuario de MongoDB propio, con permiso solo sobre quesoysabor_inventory
    client = AsyncIOMotorClient(leer_secreto_vault("quesoysabor/db/inventory")["uri"])
    coll = client[DB_NAME]["productos"]
    yield
    client.close()


app = FastAPI(title="Inventory Service", lifespan=lifespan)


def verificar_llamada(x_service_key: str = Header(default="")):
    # Sin la clave del servicio nadie puede llamar directo a este backend
    if not secrets.compare_digest(x_service_key, SERVICE_KEY):
        raise HTTPException(status_code=403, detail="Llamada no autorizada")


def requiere_rol(*roles):
    # Revisa los roles que manda el gateway. Solo se confia en ellos porque
    # verificar_llamada ya comprobo que la llamada viene de un componente interno.
    def revisar(x_authenticated_roles: str = Header(default="")):
        if not set(x_authenticated_roles.split(",")) & set(roles):
            raise HTTPException(status_code=403, detail="Rol sin permiso")
    return revisar


class ProductoIn(BaseModel):
    nombre: str = Field(min_length=1, max_length=120)
    categoria: str = Field(pattern="^(madurado|fresco|especial)$")
    descripcion: str = Field(default="", max_length=1000)
    precio: int = Field(gt=0, le=10_000_000)
    oferta_pct: int = Field(default=0, ge=0, le=90)
    stock: int = Field(ge=0, le=100_000)
    activo: bool = True


class ProductoNuevo(ProductoIn):
    id: str = Field(pattern="^[a-z0-9-]{3,64}$")


class LineaStock(BaseModel):
    product_id: str = Field(max_length=64)
    cantidad: int = Field(gt=0, le=50)


class ReservaIn(BaseModel):
    items: List[LineaStock] = Field(min_length=1, max_length=30)


def precio_final(doc) -> int:
    # Se redondea a la decena, igual que los precios de oferta que muestra el frontend
    return round(doc["precio"] * (100 - doc.get("oferta_pct", 0)) / 1000) * 10


def producto_publico(doc) -> dict:
    # Lo que ve cualquier visitante. El stock exacto no sale, solo si hay o no.
    return {
        "id": doc["_id"],
        "nombre": doc["nombre"],
        "categoria": doc["categoria"],
        "descripcion": doc.get("descripcion", ""),
        "precio": doc["precio"],
        "oferta_pct": doc.get("oferta_pct", 0),
        "precio_final": precio_final(doc),
        "disponible": doc["stock"] > 0
    }


def producto_admin(doc) -> dict:
    datos = producto_publico(doc)
    datos["stock"] = doc["stock"]
    datos["activo"] = doc.get("activo", True)
    return datos


@app.get("/health", dependencies=[Depends(verificar_llamada)])
def health():
    return {"status": "OK", "service": "Inventory"}


@app.get("/products", dependencies=[Depends(verificar_llamada)])
async def listar_productos(
    categoria: Optional[str] = Query(None, pattern="^(madurado|fresco|especial)$"),
    q: Optional[str] = Query(None, max_length=100),
    en_oferta: bool = False,
    ids: Optional[str] = Query(None, max_length=1000, description="ids separados por coma")
):
    query = {"activo": True}
    if categoria:
        query["categoria"] = categoria
    if q:
        query["nombre"] = {"$regex": q, "$options": "i"}
    if en_oferta:
        query["oferta_pct"] = {"$gt": 0}
    if ids:
        query["_id"] = {"$in": ids.split(",")[:50]}
    return [producto_publico(doc) async for doc in coll.find(query).sort("nombre")]


@app.get("/products/{product_id}", dependencies=[Depends(verificar_llamada)])
async def obtener_producto(product_id: str):
    doc = await coll.find_one({"_id": product_id, "activo": True})
    if not doc:
        raise HTTPException(404, "Producto no encontrado")
    return producto_publico(doc)


@app.get("/admin/products", dependencies=[Depends(verificar_llamada), Depends(requiere_rol("admin", "dueno"))])
async def listar_productos_admin(bajo_stock: Optional[int] = Query(None, ge=0)):
    query = {}
    if bajo_stock is not None:
        query["stock"] = {"$lte": bajo_stock}
    return [producto_admin(doc) async for doc in coll.find(query).sort("nombre")]


@app.post("/admin/products", status_code=201, dependencies=[Depends(verificar_llamada), Depends(requiere_rol("admin"))])
async def crear_producto(producto: ProductoNuevo):
    datos = producto.model_dump()
    datos["_id"] = datos.pop("id")
    if await coll.find_one({"_id": datos["_id"]}):
        raise HTTPException(409, "Ya existe un producto con ese id")
    await coll.insert_one(datos)
    return producto_admin(datos)


@app.put("/admin/products/{product_id}", dependencies=[Depends(verificar_llamada), Depends(requiere_rol("admin"))])
async def actualizar_producto(product_id: str, producto: ProductoIn):
    res = await coll.update_one({"_id": product_id}, {"$set": producto.model_dump()})
    if res.matched_count == 0:
        raise HTTPException(404, "Producto no encontrado")
    return producto_admin(await coll.find_one({"_id": product_id}))


@app.delete("/admin/products/{product_id}", dependencies=[Depends(verificar_llamada), Depends(requiere_rol("admin"))])
async def eliminar_producto(product_id: str):
    # Baja logica: los pedidos antiguos guardan nombre y precio, asi el historial no se pierde
    res = await coll.update_one({"_id": product_id}, {"$set": {"activo": False}})
    if res.matched_count == 0:
        raise HTTPException(404, "Producto no encontrado")
    return {"id": product_id, "activo": False}


# Rutas internas. El gateway no las publica, solo las usa orders.

@app.post("/internal/reservar", dependencies=[Depends(verificar_llamada)])
async def reservar_stock(reserva: ReservaIn):
    ids = [linea.product_id for linea in reserva.items]
    if len(ids) != len(set(ids)):
        raise HTTPException(400, "Hay productos repetidos en el pedido")
    reservados = []
    for linea in reserva.items:
        # El filtro stock >= cantidad hace que dos compras al mismo tiempo no dejen stock negativo
        doc = await coll.find_one_and_update(
            {"_id": linea.product_id, "activo": True, "stock": {"$gte": linea.cantidad}},
            {"$inc": {"stock": -linea.cantidad}}
        )
        if doc is None:
            # Si un producto falla se devuelve lo que ya se habia descontado
            for anterior in reservados:
                await coll.update_one({"_id": anterior["product_id"]}, {"$inc": {"stock": anterior["cantidad"]}})
            existe = await coll.find_one({"_id": linea.product_id, "activo": True})
            if not existe:
                raise HTTPException(404, f"Producto {linea.product_id} no existe")
            raise HTTPException(409, f"Sin stock suficiente de {linea.product_id}")
        reservados.append({
            "product_id": linea.product_id,
            "nombre": doc["nombre"],
            "cantidad": linea.cantidad,
            "precio_unitario": precio_final(doc)
        })
    return {"items": reservados}


@app.post("/internal/liberar", dependencies=[Depends(verificar_llamada)])
async def liberar_stock(reserva: ReservaIn):
    for linea in reserva.items:
        await coll.update_one({"_id": linea.product_id}, {"$inc": {"stock": linea.cantidad}})
    return {"message": "Stock devuelto"}
