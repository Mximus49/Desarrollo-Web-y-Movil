# Carga los datos de prueba: productos del catalogo, usuarios de cada rol y el perfil de un cliente.
# Todo es ficticio. Las contrasenas de prueba sirven solo para el ambiente local.
# Se corre despues de crear_bd.py, con la terminal preparada con: . .\scripts\entorno.ps1
#
# Uso: python scripts/datos_prueba.py

import hashlib
import os
import secrets
import sys

import httpx
from pymongo import MongoClient

VAULT_ADDR = os.getenv("VAULT_ADDR", "https://127.0.0.1:8200").rstrip("/")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")

PRODUCTOS = [
    ("mantecoso-anejo", "Mantecoso Añejo", "madurado", 6990, 15, 40),
    ("chanco-ahumado", "Chanco Ahumado", "madurado", 5490, 20, 35),
    ("reserva-cabra", "Reserva de Cabra", "especial", 7290, 0, 12),
    ("quesillo-fresco", "Quesillo Fresco", "fresco", 3990, 0, 50),
    ("crema-natural", "Queso Crema Natural", "fresco", 4290, 0, 30),
    ("manchego-reserva", "Manchego Reserva", "madurado", 8900, 10, 18),
    ("azul-andino", "Azul Andino", "especial", 9490, 25, 3),
    ("especiado-hierbas", "Especiado a las Hierbas", "especial", 6490, 0, 0),
]

USUARIOS = [
    ("ana@quesoysabor.cl", "Ana Rojas", "Ana12345", ["cliente"]),
    ("pedro@quesoysabor.cl", "Pedro Soto", "Pedro12345", ["cliente"]),
    ("admin@quesoysabor.cl", "Administrador", "Admin12345", ["admin"]),
    ("despacho@quesoysabor.cl", "Encargado Despacho", "Despacho12345", ["despacho"]),
    ("dueno@quesoysabor.cl", "Dueno Queso y Sabor", "Dueno12345", ["dueno"]),
    ("cajero@quesoysabor.cl", "Cajero Virtual", "Cajero12345", ["cajero"]),
]


def hash_password(password: str) -> str:
    # Mismo formato que hash_password de auth_service.py
    sal = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), sal, 200_000)
    return f"pbkdf2$200000${sal.hex()}${digest.hex()}"


def main():
    if not VAULT_TOKEN:
        sys.exit("VAULT_TOKEN no esta configurado. Prepare la terminal con . .\\scripts\\entorno.ps1")
    r = httpx.get(f"{VAULT_ADDR}/v1/secret/data/quesoysabor/mongo-admin", headers={"X-Vault-Token": VAULT_TOKEN}, timeout=5.0)
    r.raise_for_status()
    admin = r.json()["data"]["data"]
    client = MongoClient("127.0.0.1", 27018, username=admin["usuario"], password=admin["clave"],
                         authSource="admin", serverSelectionTimeoutMS=5000)

    productos = client["quesoysabor_inventory"]["productos"]
    for pid, nombre, categoria, precio, oferta, stock in PRODUCTOS:
        productos.update_one({"_id": pid}, {"$set": {
            "nombre": nombre, "categoria": categoria, "descripcion": f"{nombre} artesanal de Queso & Sabor",
            "precio": precio, "oferta_pct": oferta, "stock": stock, "activo": True
        }}, upsert=True)
    print(f"Productos cargados: {len(PRODUCTOS)}")

    usuarios = client["quesoysabor_auth"]["usuarios"]
    for email, nombre, password, roles in USUARIOS:
        usuarios.update_one({"email": email}, {"$set": {
            "nombre": nombre, "password_hash": hash_password(password), "roles": roles, "activo": True
        }}, upsert=True)
        print(f"Usuario: {email} ({', '.join(roles)})")

    # Ana tiene perfil completo para poder pedir despacho. Pedro no, para probar el error.
    ana = usuarios.find_one({"email": "ana@quesoysabor.cl"})
    client["quesoysabor_clients"]["clientes"].update_one({"_id": str(ana["_id"])}, {"$set": {
        "email": ana["email"], "nombre": "Ana Rojas", "rut": "11111111-1", "telefono": "+56911112222",
        "direccion": "Av. Providencia 1234, depto 5", "comuna": "Providencia", "provincia": "Santiago",
        "region": "Metropolitana de Santiago", "fecha_nacimiento": "1995-04-12", "sexo": "F"
    }}, upsert=True)
    print("Perfil de cliente cargado para ana@quesoysabor.cl")


if __name__ == "__main__":
    main()
