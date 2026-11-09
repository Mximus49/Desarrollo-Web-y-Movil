# Simula a la pasarela de pagos avisando el resultado de un pago.
# Firma el aviso con la clave webhook_secret que esta en Vault, como lo haria el proveedor real.
# Requiere la terminal preparada con: . .\scripts\entorno.ps1 (Vault y certificados)
#
# Uso: python scripts/pasarela_simulada.py --pago <payment_id> --monto <monto>
#      agregar --rechazar para simular un pago rechazado
#      agregar --evento <id> para repetir un aviso y probar que no se procesa dos veces

import argparse
import hashlib
import hmac
import json
import os
import uuid

import httpx

VAULT_ADDR = os.getenv("VAULT_ADDR", "https://127.0.0.1:8200").rstrip("/")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
GATEWAY_URL = os.getenv("GATEWAY_URL", "https://localhost:8000")


def main():
    parser = argparse.ArgumentParser(description="Pasarela de pagos simulada")
    parser.add_argument("--pago", required=True)
    parser.add_argument("--monto", required=True, type=int)
    parser.add_argument("--rechazar", action="store_true")
    parser.add_argument("--evento", default=None)
    args = parser.parse_args()

    if not VAULT_TOKEN:
        parser.error("VAULT_TOKEN no esta configurado")
    r = httpx.get(f"{VAULT_ADDR}/v1/secret/data/quesoysabor/pasarela", headers={"X-Vault-Token": VAULT_TOKEN}, timeout=5.0)
    r.raise_for_status()
    clave = r.json()["data"]["data"]["webhook_secret"]

    aviso = {
        "evento_id": args.evento or f"evt-{uuid.uuid4().hex}",
        "payment_id": args.pago,
        "estado": "RECHAZADO" if args.rechazar else "APROBADO",
        "monto": args.monto,
    }
    cuerpo = json.dumps(aviso).encode()
    firma = hmac.new(clave.encode(), cuerpo, hashlib.sha256).hexdigest()
    respuesta = httpx.post(
        f"{GATEWAY_URL}/api/payments/webhook",
        content=cuerpo,
        headers={"Content-Type": "application/json", "X-Firma": firma},
        timeout=10.0,
    )
    print(f"Aviso enviado: {aviso}")
    print(f"Respuesta {respuesta.status_code}: {respuesta.text}")


if __name__ == "__main__":
    main()
