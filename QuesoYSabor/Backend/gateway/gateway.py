from collections import defaultdict, deque
from contextlib import asynccontextmanager
import json
import os
import re
import time
import uuid

import httpx
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# API Gateway de Queso & Sabor. Es lo unico que se expone hacia afuera.
# No reenvia cualquier /api/{path}: solo deja pasar las rutas y verbos que estan en la tabla RUTAS.
# Escucha con TLS y llama a los servicios internos tambien con TLS.

VAULT_ADDR = os.getenv("VAULT_ADDR", "https://127.0.0.1:8200").rstrip("/")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")

SERVICIOS = {
    "auth": os.getenv("AUTH_SERVICE_URL", "https://127.0.0.1:8100"),
    "inventory": os.getenv("INVENTORY_URL", "https://127.0.0.1:9001"),
    "orders": os.getenv("ORDERS_URL", "https://127.0.0.1:9002"),
    "clients": os.getenv("CLIENTS_URL", "https://127.0.0.1:9003"),
    "payments": os.getenv("PAYMENTS_URL", "https://127.0.0.1:9004"),
    "analytics": os.getenv("ANALYTICS_URL", "https://127.0.0.1:9005"),
    "graphql": os.getenv("GRAPHQL_URL", "https://127.0.0.1:8090"),
}

if not VAULT_TOKEN:
    raise RuntimeError("VAULT_TOKEN no esta configurado")

PUBLICA = None
CUALQUIERA = ["cliente", "admin", "despacho", "dueno", "cajero"]

# Cada fila: id, verbo, ruta externa, servicio, ruta interna, roles permitidos.
# PUBLICA significa que no pide token. Lo que no esta aqui responde 404.
RUTAS = [
    ("G01", "POST", "/api/auth/login", "auth", "/login", PUBLICA),
    ("G02", "POST", "/api/auth/register", "auth", "/register", PUBLICA),
    ("G03", "POST", "/api/auth/logout", "auth", "/logout", CUALQUIERA),
    ("G04", "GET", "/api/auth/me", "auth", None, CUALQUIERA),
    ("G05", "GET", "/api/products", "inventory", "/products", PUBLICA),
    ("G06", "GET", "/api/products/{id}", "inventory", "/products/{id}", PUBLICA),
    ("G07", "GET", "/api/admin/products", "inventory", "/admin/products", ["admin", "dueno"]),
    ("G08", "POST", "/api/admin/products", "inventory", "/admin/products", ["admin"]),
    ("G09", "PUT", "/api/admin/products/{id}", "inventory", "/admin/products/{id}", ["admin"]),
    ("G10", "DELETE", "/api/admin/products/{id}", "inventory", "/admin/products/{id}", ["admin"]),
    ("G11", "GET", "/api/clients/me", "clients", "/clients/me", ["cliente"]),
    ("G12", "PUT", "/api/clients/me", "clients", "/clients/me", ["cliente"]),
    ("G13", "GET", "/api/admin/clients", "clients", "/admin/clients", ["admin"]),
    ("G14", "POST", "/api/orders", "orders", "/orders", ["cliente"]),
    ("G15", "GET", "/api/orders/mine", "orders", "/orders/mine", ["cliente"]),
    ("G16", "GET", "/api/orders/{id}", "orders", "/orders/{id}", ["cliente", "admin", "despacho"]),
    ("G17", "POST", "/api/orders/{id}/cancel", "orders", "/orders/{id}/cancel", ["cliente", "admin"]),
    ("G18", "GET", "/api/admin/orders", "orders", "/admin/orders", ["admin", "despacho"]),
    ("G19", "PATCH", "/api/admin/orders/{id}/estado", "orders", "/admin/orders/{id}/estado", ["admin", "despacho"]),
    ("G20", "POST", "/api/payments", "payments", "/payments", ["cliente"]),
    ("G21", "GET", "/api/payments/{id}", "payments", "/payments/{id}", ["cliente", "admin"]),
    ("G22", "POST", "/api/payments/webhook", "payments", "/payments/webhook", PUBLICA),
    ("G23", "GET", "/api/analytics/ventas", "analytics", "/analytics/ventas", ["admin", "dueno"]),
    ("G24", "POST", "/api/graphql", "graphql", "/graphql", CUALQUIERA),
    ("G25", "GET", "/api/admin/users", "auth", "/admin/users", ["admin"]),
    ("G26", "POST", "/api/admin/users", "auth", "/admin/users", ["admin"]),
    ("G27", "DELETE", "/api/admin/users/{id}", "auth", "/admin/users/{id}", ["admin"]),
    ("G28", "POST", "/api/admin/clients", "clients", "/admin/clients", ["admin"]),
    ("G29", "GET", "/api/admin/orders/imprimir", "orders", "/admin/orders/imprimir", ["admin", "despacho"]),
    ("G30", "GET", "/api/admin/caja", "orders", "/admin/caja", ["admin", "cajero", "dueno"]),
    ("G31", "POST", "/api/admin/orders/{id}/boleta", "orders", "/admin/orders/{id}/boleta", ["admin", "cajero"]),
]

# Limite de intentos por IP para las rutas que se pueden atacar por fuerza bruta
LIMITES = {"G01": 5, "G02": 5, "G22": 30}
intentos = defaultdict(deque)

CLAVES = {}
http = None  # cliente HTTP compartido: reutiliza conexiones TLS en vez de abrir una por solicitud


def compilar(patron: str):
    return re.compile("^" + re.sub(r"\{(\w+)\}", r"(?P<\1>[A-Za-z0-9_-]{1,64})", patron) + "$")


TABLA = [(rid, metodo, compilar(externa), servicio, interna, roles) for rid, metodo, externa, servicio, interna, roles in RUTAS]


def leer_claves_vault():
    for servicio in SERVICIOS:
        response = httpx.get(
            f"{VAULT_ADDR}/v1/secret/data/quesoysabor/{servicio}",
            headers={"X-Vault-Token": VAULT_TOKEN},
            timeout=5.0
        )
        if response.status_code != 200:
            raise RuntimeError(f"No fue posible leer la clave de {servicio} desde Vault")
        CLAVES[servicio] = response.json()["data"]["data"]["service_key"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    global http
    leer_claves_vault()
    http = httpx.AsyncClient(timeout=10.0, limits=httpx.Limits(max_connections=200))
    yield
    await http.aclose()


app = FastAPI(title="Queso & Sabor API Gateway", lifespan=lifespan)
security = HTTPBearer(auto_error=False)


@app.middleware("http")
async def registrar(request: Request, call_next):
    # Log con identificador de correlacion. No se escriben tokens ni cuerpos.
    request_id = uuid.uuid4().hex[:12]
    request.state.request_id = request_id
    inicio = time.perf_counter()
    response = await call_next(request)
    ms = (time.perf_counter() - inicio) * 1000
    print(f"[{request_id}] {request.method} {request.url.path} -> {response.status_code} ({ms:.0f} ms)")
    response.headers["X-Request-Id"] = request_id
    return response


def buscar_ruta(metodo: str, path: str):
    existe_otro_verbo = False
    for rid, m, regex, servicio, interna, roles in TABLA:
        match = regex.match(path)
        if match:
            if m == metodo:
                destino = interna.format(**match.groupdict()) if interna else None
                return rid, servicio, destino, roles
            existe_otro_verbo = True
    if existe_otro_verbo:
        raise HTTPException(405, "Verbo no permitido en esta ruta")
    raise HTTPException(404, "Ruta no encontrada")


def revisar_limite(rid: str, clave: str):
    if rid not in LIMITES:
        return
    ventana = intentos[(rid, clave)]
    ahora = time.time()
    while ventana and ahora - ventana[0] > 60:
        ventana.popleft()
    if len(ventana) >= LIMITES[rid]:
        raise HTTPException(429, "Demasiados intentos, espere un minuto")
    ventana.append(ahora)


async def introspect(token: str) -> dict:
    try:
        response = await http.post(
            f"{SERVICIOS['auth']}/introspect",
            json={"token": token},
            headers={"X-Service-Key": CLAVES["auth"]},
            timeout=5.0
        )
    except httpx.RequestError:
        raise HTTPException(502, "Error consultando Authentication Service")
    identity = response.json()
    if not identity.get("active", False):
        raise HTTPException(401, "Token invalido o expirado")
    return identity


@app.get("/health")
async def health():
    estado = {}
    for servicio, url in SERVICIOS.items():
        try:
            r = await http.get(f"{url}/health", headers={"X-Service-Key": CLAVES[servicio]}, timeout=2.0)
            estado[servicio] = "OK" if r.status_code == 200 else f"HTTP {r.status_code}"
        except httpx.RequestError:
            estado[servicio] = "SIN RESPUESTA"
    return {"gateway": "OK", "servicios": estado}


@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def proxy(request: Request, credentials: HTTPAuthorizationCredentials | None = Depends(security)):
    rid, servicio, destino, roles = buscar_ruta(request.method, request.url.path)
    body = await request.body()
    clave_limite = request.client.host
    if rid == "G01":
        # En el login el limite va por IP y correo, asi un usuario no bloquea a otros de la misma red
        try:
            clave_limite += "|" + str(json.loads(body).get("email", "")).lower()
        except (ValueError, AttributeError):
            pass
    revisar_limite(rid, clave_limite)

    # Las cabeceras de identidad se arman aqui. Las que mande el navegador se descartan
    # porque no se copia ninguna cabecera del request original salvo las listadas.
    headers = {"X-Service-Key": CLAVES[servicio], "X-Request-Id": request.state.request_id}
    identity = None
    if roles is not PUBLICA:
        if credentials is None:
            raise HTTPException(401, "Bearer token requerido")
        identity = await introspect(credentials.credentials)
        if not set(identity["roles"]) & set(roles):
            raise HTTPException(403, "Su rol no tiene permiso para esta operacion")
        headers["X-Authenticated-User-Id"] = identity["user_id"]
        headers["X-Authenticated-User"] = identity["email"]
        headers["X-Authenticated-Roles"] = ",".join(identity["roles"])

    if rid == "G04":
        return {k: identity[k] for k in ("user_id", "email", "nombre", "roles", "expires_at")}

    if rid == "G03":
        body = json.dumps({"token": credentials.credentials}).encode()
        headers["Content-Type"] = "application/json"
    elif request.headers.get("content-type"):
        headers["Content-Type"] = request.headers["content-type"]
    if rid == "G22":
        headers["X-Firma"] = request.headers.get("x-firma", "")

    try:
        upstream = await http.request(
            method=request.method,
            url=f"{SERVICIOS[servicio]}{destino}",
            params=request.query_params,
            content=body,
            headers=headers
        )
    except httpx.RequestError:
        raise HTTPException(502, f"Servicio {servicio} no disponible")

    response_headers = {}
    if "content-type" in upstream.headers:
        response_headers["content-type"] = upstream.headers["content-type"]
    return Response(content=upstream.content, status_code=upstream.status_code, headers=response_headers)


@app.exception_handler(HTTPException)
async def error_controlado(request: Request, exc: HTTPException):
    # Respuestas de error cortas, sin detalles internos
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})
