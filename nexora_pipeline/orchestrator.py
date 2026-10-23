# -*- coding: utf-8 -*-
"""
Coordinador determinista de la pipeline Nexora.

Encadena las 4 etapas en orden estricto y escribe el estado completo en JSON:

    Scraper (1)  →  Ordenador (2)  →  Auditor (3)  →  QA / Producción (4)

Este script es la "mínima versión ejecutable" del pipeline. En el entorno de
DeepSeek Harness, cada etapa puede estar a cargo de un agente LLM que usa los
módulos de `lib/` como herramientas y añade criterio (p. ej. el Scraper puede
buscar nuevos prospectos en la web antes de normalizarlos).

Uso:
    python orchestrator.py                          # usa data/prospectos.json
    python orchestrator.py --entrada data/prospectos.csv
    python orchestrator.py --url https://nexora.com/prototipo  # auditoría remota
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path

# Permite ejecutar desde cualquier directorio.
sys.path.insert(0, str(Path(__file__).resolve().parent))

# Salida en UTF-8 para evitar errores de codificación en consolas Windows
# (cp1252 no puede representar emojis como ✅/⚠️).
for _flujo in (sys.stdout, sys.stderr):
    if hasattr(_flujo, "reconfigure"):
        _flujo.reconfigure(encoding="utf-8", errors="replace")

from lib import auditor, linter, qa, scraper  # noqa: E402
from lib.html_board import generar_tablero  # noqa: E402
from lib.messages import (  # noqa: E402
    ETIQUETA_NICHO,
    generar_enlace_whatsapp,
    generar_mensaje,
)


def ejecutar(entrada: str, salida_dir: str, url: str | None = None) -> dict:
    """Ejecuta las 4 etapas y devuelve el estado completo del pipeline."""
    salida = Path(salida_dir)
    salida.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Etapa 1 · AGENTE 1 (Buscador/Scraper)
    # Carga/normaliza prospectos, genera mensajes y enlaces, y crea el
    # tablero HTML interactivo.
    # ------------------------------------------------------------------
    prospectos = scraper.cargar_prospectos(entrada)
    registros = []
    for p in prospectos:
        mensaje = generar_mensaje(p)
        registros.append(
            {
                "nombre": p.nombre,
                "nicho": p.nicho,
                "nicho_etiqueta": ETIQUETA_NICHO[p.nicho],
                "telefono": p.telefono,
                "web": p.web,
                "url": p.url,
                "email": p.email,
                "contacto": p.contacto,
                "tipo_contacto": p.tipo_contacto,
                "fuente": p.fuente,
                "estado_contacto": p.estado_contacto,
                "fecha_envio": p.fecha_envio,
                "mensaje": mensaje,
                "palabras": len(mensaje.split()),
                "enlace_wa": generar_enlace_whatsapp(p.telefono, mensaje),
            }
        )
    tablero = salida / "prospeccion_nexora.html"
    generar_tablero(registros, str(tablero))

    # ------------------------------------------------------------------
    # Etapa 2 · AGENTE 2 (Ordenador de Código)
    # Revisa la estructura HTML/Tailwind y ordena las carpetas.
    # ------------------------------------------------------------------
    reporte_ordenador = linter.analizar_html(str(tablero))
    orden_carpetas = linter.ordenar_carpetas(str(salida))

    # ------------------------------------------------------------------
    # Etapa 3 · AGENTE 3 (Auditor Técnico)
    # Rendimiento (peso/carga), SEO básico y SSL.
    # ------------------------------------------------------------------
    reporte_auditor = auditor.auditar(str(tablero), url=url)

    # ------------------------------------------------------------------
    # Etapa 4 · AGENTE 4 (Supervisor de Producción / QA final)
    # Enlaces rotos, Lorem Ipsum, responsive y veredicto de entrega.
    # ------------------------------------------------------------------
    reporte_qa = qa.auditar_qa(str(tablero))

    # ------------------------------------------------------------------
    # Estado consolidado que se comparte entre agentes (contrato de datos).
    # ------------------------------------------------------------------
    estado = {
        "run_id": datetime.now().strftime("%Y%m%d-%H%M%S"),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "nichos_objetivo": ["mecanica", "clinica", "ingenieria"],
        "nichos_procesados": sorted({p.nicho for p in prospectos}),
        "total_prospectos": len(prospectos),
        "prospectos": [asdict(p) for p in prospectos],
        "mensajes": registros,
        "tablero_html": str(tablero),
        "ordenador": reporte_ordenador,
        "orden_carpetas": orden_carpetas,
        "auditor": reporte_auditor,
        "qa": reporte_qa,
    }

    archivo_estado = salida / "reportes" / "pipeline_state.json"
    archivo_estado.parent.mkdir(parents=True, exist_ok=True)
    archivo_estado.write_text(
        json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return estado


def _resumen(estado: dict) -> None:
    """Imprime un resumen legible del resultado del pipeline."""
    sep = "=" * 70
    print(f"\n{sep}")
    print(f"PIPELINE NEXORA · run {estado['run_id']}")
    print(sep)
    print(f"Prospectos: {estado['total_prospectos']}  |  "
          f"Nichos: {', '.join(estado['nichos_procesados'])}")
    print(f"Tablero: {estado['tablero_html']}")
    print(f"[1 Scraper]    mensajes generados: {len(estado['mensajes'])}")
    print(f"[2 Ordenador]  estado: {estado['ordenador']['estado']} "
          f"({len(estado['ordenador']['problemas'])} problemas)")
    print(f"[3 Auditor]    peso local: {estado['auditor']['rendimiento_local']['estado']}  |  "
          f"SEO título: {'ok' if estado['auditor']['seo']['titulo_ok'] else 'revisar'}")
    print(f"[4 QA]         enlaces rotos: {len(estado['qa']['enlaces']['enlaces_rotos'])}  |  "
          f"Lorem: {'sí' if estado['qa']['lorem_ipsum_detectado'] else 'no'}  |  "
          f"responsive: {'sí' if estado['qa']['responsive'] else 'no'}")
    veredicto = "LISTO PARA ENTREGAR ✅" if estado["qa"]["listo_para_entregar"] else "PENDIENTE ⚠️"
    print(f"VEREDICTO: {veredicto}")
    for bloqueo in estado["qa"]["bloqueos"]:
        print(f"  - {bloqueo}")
    print(sep + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Ejecuta la pipeline Nexora (Scraper→Ordenador→Auditor→QA)."
    )
    ap.add_argument("--entrada", default="data/prospectos.json",
                    help="Ruta al JSON/CSV de prospectos (por defecto data/prospectos.json).")
    ap.add_argument("--salida", default="salida",
                    help="Directorio de salida (por defecto salida/).")
    ap.add_argument("--url", default=None,
                    help="URL pública del prototipo para auditoría remota (SSL/carga).")
    args = ap.parse_args()

    estado = ejecutar(args.entrada, args.salida, args.url)
    _resumen(estado)
    return 0


if __name__ == "__main__":
    sys.exit(main())
