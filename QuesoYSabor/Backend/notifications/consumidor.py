# Consumidor de avisos de pedidos (STOMP).
# orders publica en /queue/pedidos cuando un pedido se paga, cambia de estado o se anula.
# Aqui se arma el correo (con la boleta digital cuando corresponde, RF8), se envia por la API de
# mensajeria y se registra el envio en MongoDB (bandeja_salida).
# Si el broker se cae, el consumidor se reconecta solo; los mensajes esperan en la cola.
#
# Uso: python consumidor.py   (con VAULT_ADDR y VAULT_TOKEN definidos)

from datetime import datetime, timezone
import json
import os
import time

import httpx
import stomp
from pymongo import MongoClient

DESTINO = "/queue/pedidos"
VAULT_ADDR = os.getenv("VAULT_ADDR", "https://127.0.0.1:8200").rstrip("/")
VAULT_TOKEN = os.getenv("VAULT_TOKEN")
AUTH_URL = os.getenv("AUTH_SERVICE_URL", "https://127.0.0.1:8100")
MENSAJERIA_URL = os.getenv("MENSAJERIA_URL", "https://127.0.0.1:8300")
STOMP_HOST = os.getenv("STOMP_HOST", "127.0.0.1")
STOMP_PORT = int(os.getenv("STOMP_PORT", "61613"))
# RabbitMQ usa el vhost "/", otros brokers pueden pedir otro valor
STOMP_VHOST = os.getenv("STOMP_VHOST", "/")
ESPERA_REINTENTO = 5

ASUNTOS = {
    "pedido_pagado": "Boleta electronica N° {folio} - Queso & Sabor",
    "cambio_estado": "Tu pedido {order_id} ahora esta {estado}",
    "pedido_anulado": "Tu pedido {order_id} fue anulado",
}


def leer_secreto_vault(ruta: str) -> dict:
    response = httpx.get(
        f"{VAULT_ADDR}/v1/secret/data/{ruta}",
        headers={"X-Vault-Token": VAULT_TOKEN},
        timeout=5.0
    )
    if response.status_code != 200:
        raise RuntimeError(f"No fue posible leer {ruta} desde Vault")
    return response.json()["data"]["data"]


def armar_texto(evento: dict, nombre: str) -> str:
    if evento["tipo"] == "pedido_pagado":
        b = evento["boleta"]
        lineas = "\n".join(f"  {i['cantidad']} x {i['nombre']:<28} ${i['subtotal']:>9,}" for i in evento["items"])
        return (f"Hola {nombre}:\n\nRecibimos el pago de tu pedido {evento['order_id']}.\n\n"
                f"BOLETA ELECTRONICA N° {b['folio']}\nCaja {b['caja']} - emitida por {b['emitida_por']}\n"
                f"Fecha: {b['fecha'][:19].replace('T', ' ')} UTC\n\n{lineas}\n\n"
                f"  Neto  ${b['neto']:>9,}\n  IVA   ${b['iva']:>9,}\n  Total ${b['total']:>9,}\n\n"
                "Gracias por comprar en Queso & Sabor.").replace(",", ".")
    if evento["tipo"] == "cambio_estado":
        return f"Hola {nombre}:\n\nTu pedido {evento['order_id']} ahora esta {evento['estado']}."
    return f"Hola {nombre}:\n\nTu pedido {evento['order_id']} fue anulado."


class Escuchador(stomp.ConnectionListener):
    def __init__(self, conexion, coll, claves):
        self.conexion = conexion
        self.coll = coll
        self.claves = claves
        self.http = httpx.Client(timeout=10.0)

    def on_error(self, frame):
        print(f"ERROR del broker: {frame.body}")

    def on_disconnected(self):
        print("Conexion STOMP cerrada")

    def procesar(self, evento: dict):
        asunto = ASUNTOS[evento["tipo"]].format(**evento)
        # El correo no viaja en la cola: se consulta a auth solo al momento de enviar
        r = self.http.get(f"{AUTH_URL}/internal/users/{evento['user_id']}", headers={"X-Service-Key": self.claves["auth"]})
        registro = {"user_id": evento["user_id"], "tipo": evento["tipo"], "order_id": evento["order_id"],
                    "asunto": asunto, "creado": datetime.now(timezone.utc)}
        if r.status_code == 404:
            self.coll.insert_one({**registro, "texto": "", "estado": "SIN_CORREO"})
            return
        r.raise_for_status()
        usuario = r.json()
        texto = armar_texto(evento, usuario["nombre"])
        envio = self.http.post(f"{MENSAJERIA_URL}/v1/enviar",
                               json={"para": usuario["email"], "asunto": asunto, "texto": texto},
                               headers={"Authorization": f"Bearer {self.claves['mensajeria']}"})
        envio.raise_for_status()
        self.coll.insert_one({**registro, "texto": texto, "estado": "ENVIADO", "message_id": envio.json()["message_id"]})
        print(f"[CORREO ENVIADO] {evento['tipo']} pedido {evento['order_id']}")

    def on_message(self, frame):
        # STOMP 1.2 manda "ack"; algunos brokers solo mandan "message-id"
        ack_id = frame.headers.get("ack", frame.headers.get("message-id"))
        try:
            evento = json.loads(frame.body)
            ASUNTOS[evento["tipo"]]
        except (ValueError, KeyError, TypeError):
            print("[MENSAJE NO VALIDO] se descarta")
            self.conexion.nack(id=ack_id, requeue="false")
            return
        try:
            self.procesar(evento)
            self.conexion.ack(id=ack_id)
        except (httpx.HTTPError, KeyError) as exc:
            # auth o la mensajeria no respondieron: el mensaje vuelve a la cola para reintentar
            print(f"[REINTENTO] {evento['tipo']} pedido {evento['order_id']}: {type(exc).__name__}")
            time.sleep(ESPERA_REINTENTO)
            self.conexion.nack(id=ack_id, requeue="true")


def main():
    if not VAULT_TOKEN:
        raise RuntimeError("VAULT_TOKEN no esta configurado")
    broker = leer_secreto_vault("quesoysabor/broker")
    claves = {"auth": leer_secreto_vault("quesoysabor/auth")["service_key"],
              "mensajeria": leer_secreto_vault("quesoysabor/mensajeria")["api_key"]}
    coll = MongoClient(leer_secreto_vault("quesoysabor/db/notifications")["uri"])["quesoysabor_notifications"]["bandeja_salida"]

    try:
        while True:
            conexion = stomp.Connection12([(STOMP_HOST, STOMP_PORT)], vhost=STOMP_VHOST)
            conexion.set_listener("pedidos", Escuchador(conexion, coll, claves))
            try:
                conexion.connect(broker["usuario"], broker["clave"], wait=True)
                conexion.subscribe(destination=DESTINO, id="notificaciones",
                                   ack="client-individual", headers={"prefetch-count": "1"})
                print(f"Escuchando {DESTINO}. Presiona Ctrl+C para salir.")
                while conexion.is_connected():
                    time.sleep(0.5)
            except stomp.exception.ConnectFailedException:
                print(f"Broker no disponible, reintento en {ESPERA_REINTENTO} s")
            time.sleep(ESPERA_REINTENTO)
    except KeyboardInterrupt:
        print("\nDeteniendo consumidor...")


if __name__ == "__main__":
    main()
