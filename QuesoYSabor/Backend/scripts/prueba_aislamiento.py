# Prueba de aislamiento de credenciales y red (lo que Postman no puede comprobar):
#   - cada token de Vault lee solo los secretos de su politica
#   - cada usuario de MongoDB accede solo a su base y MongoDB rechaza conexiones sin credenciales
#   - el gateway no acepta HTTP sin TLS y solo el gateway escucha fuera de 127.0.0.1
#
# Uso: python scripts/prueba_aislamiento.py   (escribe tambien evidencias/prueba-aislamiento.txt)
# Requiere el sistema arriba y la terminal preparada con: . .\scripts\entorno.ps1 (token de administracion)

from datetime import datetime
from pathlib import Path
import os

import httpx
import psutil
from pymongo import MongoClient
from pymongo.errors import OperationFailure

VAULT_ADDR = os.getenv("VAULT_ADDR", "https://127.0.0.1:8200").rstrip("/")
ROOT = {"X-Vault-Token": os.getenv("VAULT_TOKEN", "")}
EVIDENCIA = Path(__file__).resolve().parent.parent / "evidencias" / "prueba-aislamiento.txt"
lineas, resultados = [], []


def check(nombre, cond):
    resultados.append(bool(cond))
    texto = f"  [{'OK' if cond else 'FALLA'}] {nombre}"
    print(texto)
    lineas.append(texto)


def titulo(texto):
    print(texto)
    lineas.append(texto)


def token_de(politica: str) -> dict:
    r = httpx.post(f"{VAULT_ADDR}/v1/auth/token/create", headers=ROOT, json={"policies": [f"quesoysabor-{politica}"], "ttl": "5m"})
    return {"X-Vault-Token": r.json()["auth"]["client_token"]}


def puede_leer(token: dict, ruta: str) -> bool:
    return httpx.get(f"{VAULT_ADDR}/v1/secret/data/quesoysabor/{ruta}", headers=token).status_code == 200


def leer(ruta: str) -> dict:
    return httpx.get(f"{VAULT_ADDR}/v1/secret/data/quesoysabor/{ruta}", headers=ROOT).json()["data"]["data"]


def main():
    titulo(f"Prueba de aislamiento de credenciales y red ({datetime.now():%Y-%m-%d %H:%M})")

    titulo("\n1. Politicas de Vault (un token por servicio)")
    casos = [("payments", "pasarela", True), ("orders", "pasarela", False), ("analytics", "payments", False),
             ("inventory", "db/orders", False), ("gateway", "db/auth", False), ("gateway", "pasarela", False),
             ("graphql", "db/inventory", False), ("notifications", "mensajeria", True), ("clients", "db/clients", True),
             ("auth", "mongo-admin", False)]
    for politica, ruta, esperado in casos:
        check(f"token de {politica} {'lee' if esperado else 'NO lee'} quesoysabor/{ruta}", puede_leer(token_de(politica), ruta) == esperado)

    titulo("\n2. Usuarios de MongoDB (uno por servicio)")
    try:
        MongoClient("127.0.0.1", 27018, serverSelectionTimeoutMS=3000).quesoysabor_auth.usuarios.find_one()
        check("MongoDB rechaza consultas sin credenciales", False)
    except OperationFailure:
        check("MongoDB rechaza consultas sin credenciales", True)
    for servicio, ajena in [("inventory", "quesoysabor_auth"), ("orders", "quesoysabor_clients"), ("payments", "quesoysabor_orders")]:
        cliente = MongoClient(leer(f"db/{servicio}")["uri"], serverSelectionTimeoutMS=3000)
        propia = cliente[f"quesoysabor_{servicio}"].list_collection_names()
        check(f"qys_{servicio} accede a su base ({len(propia)} colecciones)", len(propia) > 0)
        try:
            cliente[ajena].list_collection_names()
            check(f"qys_{servicio} NO accede a {ajena}", False)
        except OperationFailure:
            check(f"qys_{servicio} NO accede a {ajena}", True)
    try:
        MongoClient(leer("db/inventory")["uri"]).quesoysabor_inventory.productos.insert_one({"nombre": "sin campos"})
        check("El validador $jsonSchema rechaza un producto incompleto", False)
    except OperationFailure:
        check("El validador $jsonSchema rechaza un producto incompleto", True)

    titulo("\n3. TLS y exposicion de red")
    try:
        httpx.get("http://localhost:8000/health", timeout=3)
        sin_tls = True
    except httpx.HTTPError:
        sin_tls = False
    check("El gateway no responde por HTTP sin TLS", not sin_tls)
    check("El gateway responde por HTTPS con el certificado de la CA local", httpx.get("https://localhost:8000/health").status_code == 200)
    escuchando = {c.laddr.port: c.laddr.ip for c in psutil.net_connections("tcp") if c.status == psutil.CONN_LISTEN}
    for puerto in [8000, 8100, 9001, 9002, 9003, 9004, 9005, 8090, 8300, 8200, 27018, 61613]:
        ip = escuchando.get(puerto, "no escucha")
        esperado = "0.0.0.0" if puerto == 8000 else "127.0.0.1"
        check(f"puerto {puerto} escucha en {ip}", ip == esperado)

    titulo(f"\nResultado: {sum(resultados)} de {len(resultados)} comprobaciones OK")
    EVIDENCIA.write_text("\n".join(lineas) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
