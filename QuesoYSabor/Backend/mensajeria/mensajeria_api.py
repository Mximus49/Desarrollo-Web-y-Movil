# Adaptador de prueba del proveedor de mensajeria (API de correo).
# Reemplaza al proveedor real en el ambiente local y conserva su contrato:
#   POST /v1/verificar  comprueba que un correo exista y este activo (RF11)
#   POST /v1/enviar     envia un correo; aqui se guarda como archivo .eml en mensajeria/enviados (RF8)
# Ambas operaciones exigen la API key del comercio (Authorization: Bearer ...), guardada en Vault.
#
# Uso: python -m uvicorn mensajeria_api:app --host 127.0.0.1 --port 8300 (con TLS, ver iniciar_servicios.ps1)

from contextlib import asynccontextmanager
from email.message import EmailMessage
from pathlib import Path
import os
import re
import secrets
import uuid

import httpx
from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel, Field

VAULT_ADDR = os.getenv("VAULT_ADDR", "https://127.0.0.1:8200").rstrip("/")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
ENVIADOS = Path(__file__).resolve().parent / "enviados"
REMITENTE = "Queso & Sabor <no-responder@quesoysabor.cl>"

# Reglas del simulador: dominios reservados que nunca existen y buzones de prueba inexistentes o inactivos
DOMINIOS_INEXISTENTES = ("example.com", "example.org", "example.net")
SUFIJOS_INEXISTENTES = (".invalid", ".test", ".example", ".local")

API_KEY = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global API_KEY
    if not VAULT_TOKEN:
        raise RuntimeError("VAULT_TOKEN no esta configurado")
    r = httpx.get(f"{VAULT_ADDR}/v1/secret/data/quesoysabor/mensajeria", headers={"X-Vault-Token": VAULT_TOKEN}, timeout=5.0)
    if r.status_code != 200:
        raise RuntimeError("No fue posible leer quesoysabor/mensajeria desde Vault")
    API_KEY = r.json()["data"]["data"]["api_key"]
    ENVIADOS.mkdir(exist_ok=True)
    yield


app = FastAPI(title="Proveedor de mensajeria (adaptador de prueba)", lifespan=lifespan)


def verificar_api_key(authorization: str = Header(default="")):
    if not secrets.compare_digest(authorization, f"Bearer {API_KEY}"):
        raise HTTPException(401, "API key invalida")


class VerificarIn(BaseModel):
    email: str = Field(max_length=254)


class EnviarIn(BaseModel):
    para: str = Field(max_length=254)
    asunto: str = Field(min_length=1, max_length=150)
    texto: str = Field(min_length=1, max_length=20_000)


def revisar_correo(email: str) -> dict:
    email = email.strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", email):
        return {"email": email, "existe": False, "activo": False, "motivo": "formato invalido"}
    buzon, dominio = email.split("@")
    if dominio in DOMINIOS_INEXISTENTES or dominio.endswith(SUFIJOS_INEXISTENTES) or buzon.startswith("noexiste"):
        return {"email": email, "existe": False, "activo": False, "motivo": "el buzon no existe"}
    if buzon.startswith("inactivo"):
        return {"email": email, "existe": True, "activo": False, "motivo": "el buzon esta desactivado"}
    return {"email": email, "existe": True, "activo": True, "motivo": None}


@app.get("/health", dependencies=[Depends(verificar_api_key)])
def health():
    return {"status": "OK", "service": "Mensajeria"}


@app.post("/v1/verificar", dependencies=[Depends(verificar_api_key)])
def verificar(datos: VerificarIn):
    return revisar_correo(datos.email)


@app.post("/v1/enviar", status_code=202, dependencies=[Depends(verificar_api_key)])
def enviar(datos: EnviarIn):
    if not revisar_correo(datos.para)["activo"]:
        raise HTTPException(422, "Destinatario inexistente o inactivo")
    message_id = uuid.uuid4().hex
    correo = EmailMessage()
    correo["From"] = REMITENTE
    correo["To"] = datos.para
    correo["Subject"] = datos.asunto
    correo["Message-ID"] = f"<{message_id}@quesoysabor.cl>"
    correo.set_content(datos.texto)
    (ENVIADOS / f"{message_id}.eml").write_bytes(bytes(correo))
    return {"message_id": message_id, "estado": "ENVIADO"}


# Autocomprobacion de las reglas del simulador: python mensajeria_api.py
if __name__ == "__main__":
    assert revisar_correo("ana@quesoysabor.cl")["activo"]
    assert not revisar_correo("noexiste1@correo.cl")["existe"]
    assert not revisar_correo("x@example.com")["existe"]
    assert not revisar_correo("x@dominio.invalid")["existe"]
    assert revisar_correo("inactivo@correo.cl") == {"email": "inactivo@correo.cl", "existe": True, "activo": False,
                                                     "motivo": "el buzon esta desactivado"}
    assert not revisar_correo("sin-arroba")["existe"]
    print("Reglas del simulador OK")
