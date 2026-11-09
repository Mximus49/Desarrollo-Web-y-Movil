# Prueba de carga reproducible contra el API Gateway.
# Mide latencia (mediana y p95), solicitudes por segundo y errores para el catalogo (anonimo)
# y para el historial de pedidos (con sesion de ana). Durante cada medicion registra el consumo
# de CPU y memoria de los procesos del backend (los que escuchan en los puertos del sistema).
#
# Uso: python scripts/prueba_carga.py --usuarios 20 --solicitudes 50
# Requiere la terminal preparada con: . .\scripts\entorno.ps1 (certificados)

import argparse
import asyncio
import os
import platform
import statistics
import threading
import time
from datetime import datetime

import httpx
import psutil

GATEWAY_URL = os.getenv("GATEWAY_URL", "https://localhost:8000")
PUERTOS = {8000, 8100, 9001, 9002, 9003, 9004, 9005, 8090, 8300}


def procesos_backend() -> list:
    pids = {c.pid for c in psutil.net_connections("tcp") if c.status == psutil.CONN_LISTEN and c.laddr.port in PUERTOS}
    return [psutil.Process(pid) for pid in pids if pid]


class Monitor:
    # Muestrea CPU (porcentaje de un nucleo, sumado entre procesos) y memoria residente cada 0,5 s
    def __init__(self):
        self.procesos = procesos_backend()
        self.cpu, self.mem = [], []
        self.activo = True
        for p in self.procesos:
            p.cpu_percent(None)
        self.hilo = threading.Thread(target=self.muestrear, daemon=True)
        self.hilo.start()

    def muestrear(self):
        while self.activo:
            time.sleep(0.5)
            cpu = mem = 0
            for p in self.procesos:
                try:
                    cpu += p.cpu_percent(None)
                    mem += p.memory_info().rss
                except psutil.Error:
                    pass
            self.cpu.append(cpu)
            self.mem.append(mem / 2**20)

    def detener(self) -> str:
        self.activo = False
        self.hilo.join()
        return (f"CPU backend promedio {statistics.mean(self.cpu):.0f}% / max {max(self.cpu):.0f}% de un nucleo | "
                f"memoria max {max(self.mem):.0f} MB ({len(self.procesos)} procesos)")


async def usuario(client, ruta, headers, cantidad, tiempos, errores):
    for _ in range(cantidad):
        inicio = time.perf_counter()
        try:
            r = await client.get(f"{GATEWAY_URL}{ruta}", headers=headers)
            if r.status_code != 200:
                errores.append(r.status_code)
        except httpx.RequestError:
            errores.append("sin respuesta")
        tiempos.append((time.perf_counter() - inicio) * 1000)


async def medir(nombre, ruta, headers, usuarios, solicitudes):
    tiempos, errores = [], []
    limites = httpx.Limits(max_connections=usuarios)
    monitor = Monitor()
    async with httpx.AsyncClient(timeout=10.0, limits=limites) as client:
        inicio = time.perf_counter()
        await asyncio.gather(*(usuario(client, ruta, headers, solicitudes, tiempos, errores) for _ in range(usuarios)))
        duracion = time.perf_counter() - inicio
    consumo = monitor.detener()
    tiempos.sort()
    p95 = tiempos[int(len(tiempos) * 0.95) - 1]
    print(f"{nombre}: {len(tiempos)} solicitudes en {duracion:.1f} s | "
          f"{len(tiempos) / duracion:.0f} req/s | mediana {statistics.median(tiempos):.0f} ms | "
          f"p95 {p95:.0f} ms | errores {len(errores)}")
    print(f"  {consumo}")


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--usuarios", type=int, default=20)
    parser.add_argument("--solicitudes", type=int, default=50)
    args = parser.parse_args()

    r = httpx.post(f"{GATEWAY_URL}/api/auth/login", json={"email": "ana@quesoysabor.cl", "password": "Ana12345"})
    token = r.json()["access_token"]
    print(f"Fecha: {datetime.now():%Y-%m-%d %H:%M} | Equipo: {platform.system()} {platform.release()}, "
          f"{psutil.cpu_count()} nucleos logicos, {psutil.virtual_memory().total / 2**30:.0f} GB RAM")
    print("Entorno: todos los servicios en la misma maquina con TLS, MongoDB y RabbitMQ en Docker, Vault en modo dev")
    print(f"Usuarios concurrentes: {args.usuarios}, solicitudes por usuario: {args.solicitudes}")
    await medir("Catalogo GET /api/products", "/api/products", {}, args.usuarios, args.solicitudes)
    await medir("Mis pedidos GET /api/orders/mine", "/api/orders/mine", {"Authorization": f"Bearer {token}"}, args.usuarios, args.solicitudes)


if __name__ == "__main__":
    asyncio.run(main())
