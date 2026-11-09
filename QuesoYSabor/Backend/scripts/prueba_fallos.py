# Prueba reproducible de fallos, desconexiones y concurrencia. Con el sistema completo arriba:
#   1. inventory caido: el pedido no se crea (503), GraphQL entrega respuesta parcial, health lo marca
#   2. broker caido: la venta sigue, el aviso queda pendiente y se entrega cuando el broker vuelve
#   3. mensajeria caida: el registro falla cerrado (503) porque no se puede validar el correo
#   4. auth caido: las rutas protegidas responden 502 y el catalogo publico sigue funcionando
#   5. compras simultaneas: con stock 2, de 10 compras al mismo tiempo solo se crean 2 pedidos
# Cada servicio detenido se vuelve a iniciar con su misma linea de comando y entorno.
#
# Uso: python scripts/prueba_fallos.py        (escribe tambien evidencias/prueba-fallos.txt)
# Requiere la terminal preparada con: . .\scripts\entorno.ps1

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
import os
import subprocess
import time
import uuid

import httpx
import psutil
from pymongo import MongoClient

GW = os.getenv("GATEWAY_URL", "https://localhost:8000")
VAULT_ADDR = os.getenv("VAULT_ADDR", "https://127.0.0.1:8200").rstrip("/")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
EVIDENCIA = Path(__file__).resolve().parent.parent / "evidencias" / "prueba-fallos.txt"
lineas, resultados = [], []


def log(texto=""):
    print(texto)
    lineas.append(texto)


def check(nombre, cond, detalle=""):
    resultados.append(bool(cond))
    log(f"  [{'OK' if cond else 'FALLA'}] {nombre}" + ("" if cond else f" -> {detalle}"))


def detener(puerto: int) -> dict:
    # Guarda como se lanzo el proceso para poder reiniciarlo igual
    pid = next(c.pid for c in psutil.net_connections("tcp") if c.status == psutil.CONN_LISTEN and c.laddr.port == puerto)
    p = psutil.Process(pid)
    datos = {"cmd": p.cmdline(), "cwd": p.cwd(), "env": p.environ()}
    p.kill()
    p.wait(10)
    return datos


def reiniciar(datos: dict, puerto: int):
    subprocess.Popen(datos["cmd"], cwd=datos["cwd"], env=datos["env"], creationflags=subprocess.CREATE_NEW_CONSOLE)
    for _ in range(40):
        time.sleep(0.5)
        if any(c.laddr.port == puerto and c.status == psutil.CONN_LISTEN for c in psutil.net_connections("tcp")):
            time.sleep(1.5)
            return
    raise RuntimeError(f"El servicio del puerto {puerto} no volvio a partir")


def login(email, clave):
    return {"Authorization": "Bearer " + httpx.post(f"{GW}/api/auth/login", json={"email": email, "password": clave}).json()["access_token"]}


def mongo():
    r = httpx.get(f"{VAULT_ADDR}/v1/secret/data/quesoysabor/mongo-admin", headers={"X-Vault-Token": VAULT_TOKEN})
    admin = r.json()["data"]["data"]
    return MongoClient("127.0.0.1", 27018, username=admin["usuario"], password=admin["clave"], authSource="admin")


def main():
    log(f"Prueba de fallos, desconexiones y concurrencia ({datetime.now():%Y-%m-%d %H:%M})")
    ana = login("ana@quesoysabor.cl", "Ana12345")
    pedido = {"items": [{"product_id": "crema-natural", "cantidad": 1}], "modalidad": "RETIRO", "local_retiro": "Local Nunoa"}
    consulta = {"query": "query($id: ID!) { resumenPedido(id: $id) { estado lineas { nombre producto { nombre } } } }"}

    log("\n1. inventory detenido")
    order_id = httpx.post(f"{GW}/api/orders", headers=ana, json=pedido).json()["id"]
    consulta["variables"] = {"id": order_id}
    inv = detener(9001)
    r = httpx.post(f"{GW}/api/orders", headers=ana, json=pedido)
    check(f"POST /api/orders -> {r.status_code} {r.json().get('detail')}", r.status_code == 503, r.text)
    r = httpx.post(f"{GW}/api/graphql", headers=ana, json=consulta).json()
    check("GraphQL responde parcial: el pedido sale y producto queda null con un error",
          r.get("data", {}).get("resumenPedido") and r["data"]["resumenPedido"]["lineas"][0]["producto"] is None and r.get("errors"), r)
    r = httpx.get(f"{GW}/api/products")
    check(f"GET /api/products -> {r.status_code} {r.json().get('detail')}", r.status_code == 502, r.text)
    r = httpx.get(f"{GW}/health").json()
    check(f"health marca inventory: {r['servicios']['inventory']}", r["servicios"]["inventory"] == "SIN RESPUESTA", r)
    reiniciar(inv, 9001)
    r = httpx.post(f"{GW}/api/graphql", headers=ana, json=consulta).json()
    check("inventory reiniciado: GraphQL vuelve a responder completo", "errors" not in r and r["data"]["resumenPedido"]["lineas"][0]["producto"], r)

    log("\n2. broker STOMP (RabbitMQ) detenido")
    db = mongo()
    subprocess.run(["docker", "stop", "quesoysabor-rabbitmq"], check=True, capture_output=True)
    r = httpx.post(f"{GW}/api/orders/{order_id}/cancel", headers=ana, json={"motivo": "Prueba de broker caido"})
    check(f"La anulacion funciona sin broker -> {r.status_code}", r.status_code == 200, r.text)
    pendientes = db.quesoysabor_orders.avisos_pendientes.count_documents({"evento.order_id": order_id})
    check(f"El aviso queda guardado en avisos_pendientes ({pendientes})", pendientes == 1)
    subprocess.run(["docker", "start", "quesoysabor-rabbitmq"], check=True, capture_output=True)
    entregado = False
    for _ in range(60):
        time.sleep(2)
        if db.quesoysabor_notifications.bandeja_salida.find_one({"order_id": order_id, "tipo": "pedido_anulado"}):
            entregado = True
            break
    check("Broker de vuelta: orders reenvia el aviso, notifications se reconecta y envia el correo", entregado)
    check("avisos_pendientes queda vacio", db.quesoysabor_orders.avisos_pendientes.count_documents({}) == 0)

    log("\n3. mensajeria detenida")
    men = detener(8300)
    r = httpx.post(f"{GW}/api/auth/register", json={"email": f"fallo{uuid.uuid4().hex[:6]}@correo.cl", "nombre": "Prueba", "password": "Prueba123"})
    check(f"Registro sin poder validar el correo -> {r.status_code} {r.json().get('detail')}", r.status_code == 503, r.text)
    reiniciar(men, 8300)

    log("\n4. auth detenido")
    auth = detener(8100)
    r = httpx.get(f"{GW}/api/orders/mine", headers=ana)
    check(f"Ruta protegida -> {r.status_code} {r.json().get('detail')}", r.status_code == 502, r.text)
    r = httpx.get(f"{GW}/api/products")
    check(f"Catalogo publico sigue disponible -> {r.status_code}", r.status_code == 200)
    reiniciar(auth, 8100)
    check("auth reiniciado: la sesion sigue valida (vive en MongoDB)", httpx.get(f"{GW}/api/orders/mine", headers=ana).status_code == 200)

    log("\n5. Compras simultaneas sobre poco stock")
    admin = login("admin@quesoysabor.cl", "Admin12345")
    httpx.put(f"{GW}/api/admin/products/reserva-cabra", headers=admin, json={
        "nombre": "Reserva de Cabra", "categoria": "especial", "descripcion": "Reserva de Cabra artesanal",
        "precio": 7290, "oferta_pct": 0, "stock": 2}).raise_for_status()
    compra = {"items": [{"product_id": "reserva-cabra", "cantidad": 1}], "modalidad": "RETIRO", "local_retiro": "Local Nunoa"}
    with ThreadPoolExecutor(10) as ejecutor:
        codigos = list(ejecutor.map(lambda _: httpx.post(f"{GW}/api/orders", headers=ana, json=compra, timeout=20).status_code, range(10)))
    stock = next(p["stock"] for p in httpx.get(f"{GW}/api/admin/products", headers=admin).json() if p["id"] == "reserva-cabra")
    check(f"10 compras simultaneas con stock 2: {codigos.count(201)} creadas, {codigos.count(409)} sin stock, stock final {stock}",
          codigos.count(201) == 2 and codigos.count(409) == 8 and stock == 0, codigos)

    log(f"\nResultado: {sum(resultados)} de {len(resultados)} comprobaciones OK")
    EVIDENCIA.write_text("\n".join(lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
