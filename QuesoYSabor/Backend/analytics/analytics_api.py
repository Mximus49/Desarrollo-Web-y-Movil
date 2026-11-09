from collections import defaultdict
from contextlib import asynccontextmanager
import os
import secrets

import httpx
from datetime import date
from typing import Optional

from fastapi import FastAPI, HTTPException, Header, Depends

# Servicio de analitica para el dueno y el administrador.
# Va separado de orders para que los reportes no compitan con la venta.
# No guarda datos propios ni datos personales: calcula sobre las ventas que entrega orders.

VAULT_ADDR = os.getenv("VAULT_ADDR", "https://127.0.0.1:8200").rstrip("/")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
ORDERS_URL = os.getenv("ORDERS_URL", "https://127.0.0.1:9002")

if not VAULT_TOKEN:
    raise RuntimeError("VAULT_TOKEN no esta configurado")

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
    SECRETOS["propia"] = leer_secreto_vault("quesoysabor/analytics")["service_key"]
    SECRETOS["orders"] = leer_secreto_vault("quesoysabor/orders")["service_key"]
    yield


app = FastAPI(title="Analytics Service", lifespan=lifespan)


def verificar_llamada(x_service_key: str = Header(default="")):
    if not secrets.compare_digest(x_service_key, SECRETOS["propia"]):
        raise HTTPException(status_code=403, detail="Llamada no autorizada")


def requiere_rol(*roles):
    def revisar(x_authenticated_roles: str = Header(default="")):
        if not set(x_authenticated_roles.split(",")) & set(roles):
            raise HTTPException(status_code=403, detail="Rol sin permiso")
    return revisar


def resumir(ventas: list) -> dict:
    por_dia = defaultdict(int)
    por_producto = defaultdict(lambda: {"nombre": "", "unidades": 0, "monto": 0})
    for venta in ventas:
        por_dia[venta["fecha"]] += venta["total"]
        for item in venta["items"]:
            fila = por_producto[item["product_id"]]
            fila["nombre"] = item["nombre"]
            fila["unidades"] += item["cantidad"]
            fila["monto"] += item["subtotal"]
    total = sum(v["total"] for v in ventas)
    ranking = sorted(
        ({"product_id": pid, **datos} for pid, datos in por_producto.items()),
        key=lambda fila: fila["unidades"], reverse=True
    )
    return {
        "pedidos_pagados": len(ventas),
        "total_vendido": total,
        "ticket_promedio": round(total / len(ventas)) if ventas else 0,
        "ventas_por_dia": [{"fecha": f, "total": t} for f, t in sorted(por_dia.items())],
        "productos_mas_vendidos": ranking[:5]
    }


@app.get("/health", dependencies=[Depends(verificar_llamada)])
def health():
    return {"status": "OK", "service": "Analytics"}


@app.get("/analytics/ventas", dependencies=[Depends(verificar_llamada), Depends(requiere_rol("admin", "dueno"))])
async def reporte_ventas(desde: Optional[date] = None, hasta: Optional[date] = None):
    if desde and hasta and desde > hasta:
        raise HTTPException(400, "La fecha desde es mayor que hasta")
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{ORDERS_URL}/internal/ventas", headers={"X-Service-Key": SECRETOS["orders"]})
    except httpx.RequestError:
        raise HTTPException(503, "orders no disponible")
    if resp.status_code != 200:
        raise HTTPException(502, "No se pudieron obtener las ventas")
    ventas = [v for v in resp.json()
              if (not desde or v["fecha"] >= desde.isoformat()) and (not hasta or v["fecha"] <= hasta.isoformat())]
    return resumir(ventas)

