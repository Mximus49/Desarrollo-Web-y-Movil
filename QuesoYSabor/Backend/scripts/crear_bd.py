# Script de creacion de la base de datos: usuarios de MongoDB por servicio, colecciones con
# validacion de esquema ($jsonSchema) e indices. Usa la credencial de administrador guardada en Vault.
#
# Uso: python scripts/crear_bd.py           crea lo que falte (se puede correr varias veces)
#      python scripts/crear_bd.py --reset   borra antes las bases de este backend
# Requiere la terminal preparada con: . .\scripts\entorno.ps1

import os
import sys
import time

import httpx
from pymongo import ASCENDING, MongoClient
from pymongo.errors import OperationFailure, ServerSelectionTimeoutError

VAULT_ADDR = os.getenv("VAULT_ADDR", "https://127.0.0.1:8200").rstrip("/")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
ENTERO = {"bsonType": ["int", "long"]}

# Esquema de cada coleccion. Lo que no cumple el validador es rechazado por MongoDB.
ESQUEMAS = {
    "quesoysabor_auth": {
        "usuarios": {
            "required": ["email", "nombre", "password_hash", "roles", "activo"],
            "properties": {
                "email": {"bsonType": "string", "pattern": "^[^@\\s]+@[^@\\s]+$"},
                "nombre": {"bsonType": "string", "maxLength": 80},
                "password_hash": {"bsonType": "string", "pattern": "^pbkdf2\\$"},
                "roles": {"bsonType": "array", "minItems": 1,
                          "items": {"enum": ["cliente", "admin", "despacho", "dueno", "cajero"]}},
                "activo": {"bsonType": "bool"},
            },
        },
        "sesiones": {
            "required": ["token_hash", "user_id", "expires_at"],
            "properties": {"token_hash": {"bsonType": "string", "minLength": 64, "maxLength": 64},
                           "user_id": {"bsonType": "string"}, "expires_at": {"bsonType": "date"}},
        },
    },
    "quesoysabor_inventory": {
        "productos": {
            "required": ["nombre", "categoria", "precio", "oferta_pct", "stock", "activo"],
            "properties": {
                "nombre": {"bsonType": "string"},
                "categoria": {"enum": ["madurado", "fresco", "especial"]},
                "precio": {**ENTERO, "minimum": 1},
                "oferta_pct": {**ENTERO, "minimum": 0, "maximum": 90},
                "stock": {**ENTERO, "minimum": 0},
                "activo": {"bsonType": "bool"},
            },
        },
    },
    "quesoysabor_clients": {
        "clientes": {
            "required": ["email", "nombre"],
            "properties": {
                "email": {"bsonType": "string"},
                "rut": {"bsonType": "string", "pattern": "^\\d{7,8}-[\\dK]$"},
                "telefono": {"bsonType": ["string", "null"]},
                "fecha_nacimiento": {"bsonType": ["string", "null"]},
                "sexo": {"enum": ["F", "M", "Otro", "No informa", None]},
            },
        },
    },
    "quesoysabor_orders": {
        "pedidos": {
            "required": ["user_id", "estado", "modalidad", "items", "total", "creado"],
            "properties": {
                "user_id": {"bsonType": "string"},
                "estado": {"enum": ["PENDIENTE_PAGO", "PAGADO", "EN_PREPARACION", "EN_REPARTO",
                                    "LISTO_RETIRO", "ENTREGADO", "ANULADO"]},
                "modalidad": {"enum": ["DESPACHO", "RETIRO"]},
                "items": {"bsonType": "array", "minItems": 1},
                "total": {**ENTERO, "minimum": 0},
                "creado": {"bsonType": "date"},
            },
        },
        "contadores": None,
        "avisos_pendientes": None,
    },
    "quesoysabor_payments": {
        "pagos": {
            "required": ["order_id", "user_id", "monto", "estado", "creado"],
            "properties": {"monto": {**ENTERO, "minimum": 0},
                           "estado": {"enum": ["PENDIENTE", "APROBADO", "RECHAZADO"]},
                           "creado": {"bsonType": "date"}},
        },
        "eventos_pasarela": {"required": ["evento_id", "recibido"], "properties": {}},
    },
    "quesoysabor_notifications": {
        "bandeja_salida": {
            "required": ["user_id", "tipo", "texto", "estado", "creado"],
            "properties": {"estado": {"enum": ["ENVIADO", "SIN_CORREO"]}},
        },
    },
}

INDICES = [
    ("quesoysabor_auth", "usuarios", [("email", ASCENDING)], {"unique": True}),
    ("quesoysabor_auth", "sesiones", [("token_hash", ASCENDING)], {}),
    ("quesoysabor_auth", "sesiones", [("expires_at", ASCENDING)], {"expireAfterSeconds": 0}),
    ("quesoysabor_clients", "clientes", [("rut", ASCENDING)], {"unique": True, "sparse": True}),
    ("quesoysabor_orders", "pedidos", [("user_id", ASCENDING)], {}),
    ("quesoysabor_orders", "pedidos", [("estado", ASCENDING), ("creado", ASCENDING)], {}),
    ("quesoysabor_payments", "pagos", [("order_id", ASCENDING)], {}),
    ("quesoysabor_payments", "eventos_pasarela", [("evento_id", ASCENDING)], {"unique": True}),
]


def leer_vault(ruta: str) -> dict:
    r = httpx.get(f"{VAULT_ADDR}/v1/secret/data/{ruta}", headers={"X-Vault-Token": VAULT_TOKEN}, timeout=5.0)
    r.raise_for_status()
    return r.json()["data"]["data"]


def conectar_admin() -> MongoClient:
    admin = leer_vault("quesoysabor/mongo-admin")
    client = MongoClient("127.0.0.1", 27018, username=admin["usuario"], password=admin["clave"],
                         authSource="admin", serverSelectionTimeoutMS=3000)
    # El contenedor tarda unos segundos en aceptar conexiones la primera vez
    for _ in range(30):
        try:
            client.admin.command("ping")
            return client
        except (ServerSelectionTimeoutError, OperationFailure):
            time.sleep(2)
    raise RuntimeError("MongoDB no responde en 127.0.0.1:27018. Revise iniciar_docker.ps1")


def main():
    if not VAULT_TOKEN:
        sys.exit("VAULT_TOKEN no esta configurado. Prepare la terminal con . .\\scripts\\entorno.ps1")
    client = conectar_admin()

    if "--reset" in sys.argv:
        for base in ESQUEMAS:
            client.drop_database(base)
            print(f"Base borrada: {base}")

    for base, colecciones in ESQUEMAS.items():
        db = client[base]
        existentes = db.list_collection_names()
        for nombre, esquema in colecciones.items():
            opciones = {}
            if esquema:
                opciones = {"validator": {"$jsonSchema": {"bsonType": "object", **esquema}},
                            "validationLevel": "strict", "validationAction": "error"}
            if nombre in existentes:
                if opciones:
                    db.command("collMod", nombre, **opciones)
            else:
                db.create_collection(nombre, **opciones)
        print(f"Colecciones de {base}: {', '.join(colecciones)}")

    for base, coleccion, claves, opciones in INDICES:
        client[base][coleccion].create_index(claves, **opciones)
    print(f"Indices creados: {len(INDICES)}")

    # Un usuario por servicio, con lectura y escritura solo sobre su propia base
    for servicio in ["auth", "inventory", "orders", "clients", "payments", "notifications"]:
        cred = leer_vault(f"quesoysabor/db/{servicio}")
        roles = [{"role": "readWrite", "db": cred["base"]}]
        try:
            client.admin.command("createUser", cred["usuario"], pwd=cred["clave"], roles=roles)
        except OperationFailure as exc:
            if exc.code != 51003:  # el usuario ya existe: se actualiza su clave y permisos
                raise
            client.admin.command("updateUser", cred["usuario"], pwd=cred["clave"], roles=roles)
        print(f"Usuario de MongoDB {cred['usuario']}: readWrite en {cred['base']}")


if __name__ == "__main__":
    main()
