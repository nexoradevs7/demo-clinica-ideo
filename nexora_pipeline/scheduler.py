# -*- coding: utf-8 -*-
"""
Programador diario de la pipeline Nexora.

Dispara la pipeline automáticamente todos los días a las 08:00 (hora local de
Venezuela, zona America/Caracas = UTC-4, sin horario de verano).

Modos de uso:
    1) Ejecución inmediata (ideal para Windows Task Scheduler o cron):
           python scheduler.py --once
    2) Daemon de larga duración (bucle interno, sin depender del SO):
           python scheduler.py --daemon
    3) Solo imprimir el comando de registro en Windows Task Scheduler:
           python scheduler.py --print-schtasks

Argumentos comunes:
    --entrada  Ruta al JSON/CSV de prospectos (def. data/prospectos.json)
    --salida   Directorio de salida (def. salida)
    --url      URL pública opcional para auditoría remota (SSL/carga)
"""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
import time
from pathlib import Path
from zoneinfo import ZoneInfo

# Salida en UTF-8 para evitar errores de codificación en consolas Windows.
for _flujo in (sys.stdout, sys.stderr):
    if hasattr(_flujo, "reconfigure"):
        _flujo.reconfigure(encoding="utf-8", errors="replace")

BASE = Path(__file__).resolve().parent
TZ = "America/Caracas"
HORA_OBJETIVO = dt.time(8, 0, 0)


def _zona() -> ZoneInfo:
    return ZoneInfo(TZ)


def proxima_ejecucion() -> dt.datetime:
    """Devuelve el próximo 08:00 (America/Caracas) a partir de ahora."""
    zona = _zona()
    ahora = dt.datetime.now(zona)
    objetivo = dt.datetime.combine(ahora.date(), HORA_OBJETIVO, tzinfo=zona)
    if objetivo <= ahora:
        objetivo += dt.timedelta(days=1)
    return objetivo


def ejecutar_pipeline(entrada: str, salida: str, url: str | None = None) -> int:
    """Invoca al coordinador (orchestrator.py) y devuelve su código de salida."""
    cmd = [
        sys.executable,
        str(BASE / "orchestrator.py"),
        "--entrada", entrada,
        "--salida", salida,
    ]
    if url:
        cmd += ["--url", url]
    return subprocess.run(cmd, cwd=str(BASE)).returncode


def modo_daemon(entrada: str, salida: str, url: str | None = None) -> None:
    """Bucle infinito: espera hasta las 08:00 y ejecuta la pipeline cada día."""
    print(f"[Scheduler] Zona horaria: {TZ}. Objetivo diario: {HORA_OBJETIVO}.")
    while True:
        objetivo = proxima_ejecucion()
        espera = (objetivo - dt.datetime.now(_zona())).total_seconds()
        print(
            f"[Scheduler] Próxima ejecución: {objetivo.isoformat(timespec='seconds')} "
            f"(en {espera / 3600:.2f} h)."
        )
        time.sleep(espera)
        print(
            f"[Scheduler] Iniciando pipeline: "
            f"{dt.datetime.now(_zona()).isoformat(timespec='seconds')}"
        )
        codigo = ejecutar_pipeline(entrada, salida, url)
        print(f"[Scheduler] Pipeline finalizada con código {codigo}.")


def print_schtasks(entrada: str, salida: str) -> None:
    """Imprime el comando para registrar la tarea diaria en Windows."""
    cmd = [
        sys.executable,
        str(BASE / "scheduler.py"),
        "--once",
        "--entrada", entrada,
        "--salida", salida,
    ]
    tr = subprocess.list2cmdline(cmd)
    print("Registra la tarea diaria (08:00, hora LOCAL de la máquina) con:")
    print()
    print(f'  schtasks /Create /TN "NexoraPipelineDiaria" /SC DAILY /ST 08:00 /F /TR "{tr}"')
    print()
    print("Nota: schtasks usa la zona horaria LOCAL del equipo. Si el equipo NO está en")
    print("America/Caracas, ajusta /ST a la hora equivalente (08:00 Caracas = 12:00 UTC).")
    print("Alternativa recomendada sin depender del SO:  python scheduler.py --daemon")


def main() -> int:
    ap = argparse.ArgumentParser(description="Programador diario de la pipeline Nexora.")
    grupo = ap.add_mutually_exclusive_group()
    grupo.add_argument("--once", action="store_true", help="Ejecuta la pipeline una sola vez.")
    grupo.add_argument("--daemon", action="store_true", help="Bucle diario a las 08:00 Caracas.")
    grupo.add_argument("--print-schtasks", action="store_true",
                       help="Imprime el comando de Windows Task Scheduler.")
    ap.add_argument("--entrada", default="data/prospectos.json")
    ap.add_argument("--salida", default="salida")
    ap.add_argument("--url", default=None)
    args = ap.parse_args()

    if args.print_schtasks:
        print_schtasks(args.entrada, args.salida)
        return 0
    if args.once:
        codigo = ejecutar_pipeline(args.entrada, args.salida, args.url)
        return codigo
    # Por defecto (o con --daemon): bucle diario.
    modo_daemon(args.entrada, args.salida, args.url)
    return 0


if __name__ == "__main__":
    sys.exit(main())
