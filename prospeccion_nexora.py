# -*- coding: utf-8 -*-
"""
============================================================================
 NEXORA · Prospección B2B — Maracaibo, Venezuela
============================================================================
 Lee prospectos.json, filtra por nicho (por defecto: "clinica")
 y genera prospeccion_nexora.html con la tabla interactiva lista.

 Uso:
     python prospeccion_nexora.py                        # solo clínicas
     python prospeccion_nexora.py --nicho mecanica
     python prospeccion_nexora.py --nicho all
     python prospeccion_nexora.py --json prospectos.json --out salida.html
============================================================================
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import urllib.parse
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------------------
# Constantes
# ---------------------------------------------------------------------------

NICHOS_VALIDOS = {"mecanica", "clinica", "ingenieria"}

ETIQUETA_NICHO = {
    "mecanica": "Mecánica",
    "clinica": "Clínica",
    "ingenieria": "Ingeniería",
}

ESTADOS_WEB_VALIDOS = {"Sin Web", "Web Lenta", "No Móvil", "Con Web"}

ARCHIVO_ENTRADA = "prospectos.json"
ARCHIVO_SALIDA = "prospeccion_nexora.html"

OFERTA = (
    "Le armo una vista previa gratuita de su web optimizada "
    "en 24 horas, sin compromiso."
)

# ---------------------------------------------------------------------------
# Modelo de datos
# ---------------------------------------------------------------------------

@dataclass
class Prospecto:
    nombre: str
    nicho: str
    telefono: str
    web: str = "Sin Web"
    url: str = ""
    email: str = ""
    contacto: str = ""
    tipo_contacto: str = "directo"
    estado_contacto: str = "pendiente"
    fuente: str = ""

    def __post_init__(self) -> None:
        self.nombre = (self.nombre or "").strip()
        self.nicho = (self.nicho or "").strip().lower()
        self.web = (self.web or "Sin Web").strip()
        self.url = (self.url or "").strip()
        self.email = (self.email or "").strip()
        self.contacto = (self.contacto or "").strip()
        self.tipo_contacto = (self.tipo_contacto or "directo").strip()
        self.estado_contacto = (self.estado_contacto or "pendiente").strip().lower()
        self.fuente = (self.fuente or "").strip()

        if self.nicho not in NICHOS_VALIDOS:
            raise ValueError(
                f"Nicho inválido para '{self.nombre}': {self.nicho!r}. "
                f"Usa uno de {sorted(NICHOS_VALIDOS)}."
            )
        if self.web not in ESTADOS_WEB_VALIDOS:
            self.web = "Sin Web"

# ---------------------------------------------------------------------------
# Mensajes y enlaces
# ---------------------------------------------------------------------------

def normalizar_numero(telefono: str) -> str:
    digitos = "".join(ch for ch in telefono if ch.isdigit())
    if not digitos:
        raise ValueError(f"El teléfono '{telefono}' no contiene dígitos.")
    return digitos


def generar_mensaje(p: Prospecto) -> str:
    nombre = p.nombre.rstrip(". ").strip()

    if p.nicho == "mecanica":
        mensaje = (
            f"Hola, {nombre}. Muchos clientes buscan repuestos o auxilio "
            "vial desde el teléfono y hoy no lo encuentran a usted. "
            f"{OFERTA} ¿Se la envío por aquí?"
        )
    elif p.nicho == "clinica":
        mensaje = (
            f"Hola, {nombre}. La confianza de un paciente se decide en "
            "segundos desde el móvil. Si agendar una cita no es rápido "
            f"y fácil, lo pierden. {OFERTA} ¿Se la envío por aquí?"
        )
    else:
        mensaje = (
            f"Hola, {nombre}. Sus proyectos hablan por usted, pero sin una "
            "web moderna no proyecta la autoridad técnica que merece. "
            f"{OFERTA} ¿Se la envío por aquí?"
        )
    return mensaje


def generar_enlace_whatsapp(telefono: str, mensaje: str) -> str:
    numero = normalizar_numero(telefono)
    return f"https://wa.me/{numero}?text={urllib.parse.quote(mensaje)}"

# ---------------------------------------------------------------------------
# Carga de prospectos desde JSON
# ---------------------------------------------------------------------------

def cargar_desde_json(ruta: str, nicho_filtro: Optional[str] = None) -> List[Prospecto]:
    with open(ruta, "r", encoding="utf-8") as f:
        data = json.load(f)

    campos_validos = set(Prospecto.__dataclass_fields__.keys())
    prospectos: List[Prospecto] = []

    for item in data.get("prospectos", []):
        limpio = {k: v for k, v in item.items() if k in campos_validos}
        p = Prospecto(**limpio)
        if nicho_filtro and p.nicho != nicho_filtro:
            continue
        prospectos.append(p)

    return prospectos

# ---------------------------------------------------------------------------
# Generación de HTML
# ---------------------------------------------------------------------------

def _fila_html(p: Prospecto) -> str:
    mensaje = generar_mensaje(p)
    enlace = generar_enlace_whatsapp(p.telefono, mensaje)
    etiqueta_nicho = ETIQUETA_NICHO[p.nicho]

    tipo_label = (
        "contacto directo" if p.tipo_contacto == "directo" else "atención general"
    )
    partes_sub = [html.escape(p.telefono), tipo_label]
    if p.email:
        partes_sub.append(
            f'<a class="mailto" href="mailto:{html.escape(p.email, quote=True)}">'
            f'{html.escape(p.email)}</a>'
        )
    sub = " · ".join(partes_sub)

    if p.web == "Con Web" and p.url:
        web_cell = (
            f'<a class="link-web" href="{html.escape(p.url, quote=True)}" '
            'target="_blank" rel="noopener">Ver web</a>'
        )
    else:
        web_cell = '<span class="sin-web">Sin web</span>'

    if p.estado_contacto == "correo_enviado":
        estado_cell = "<span class='estado estado-enviado'>Correo enviado</span>"
    else:
        estado_cell = "<span class='estado estado-pendiente'>Pendiente</span>"

    return (
        "<tr>"
        f"<td><div class='empresa'>{html.escape(p.nombre)}</div>"
        f"<div class='sub'>{sub}</div></td>"
        f"<td>{html.escape(etiqueta_nicho)}</td>"
        f"<td><span class='badge'>{html.escape(p.web)}</span></td>"
        f"<td>{web_cell}</td>"
        f"<td>{estado_cell}</td>"
        f"<td><a class='btn-wa' href='{html.escape(enlace, quote=True)}' "
        "target='_blank' rel='noopener'>Enviar WhatsApp</a></td>"
        "</tr>"
    )


def generar_html(prospectos: List[Prospecto], archivo: str = ARCHIVO_SALIDA) -> str:
    filas = "\n        ".join(_fila_html(p) for p in prospectos)

    documento = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Tablero de prospección B2B de Nexora para Maracaibo.">
<title>Nexora · Prospección B2B Maracaibo</title>
<style>
  :root {{
    --verde: #25D366;
    --verde-oscuro: #1ebe5b;
    --tinta: #1f2937;
    --gris: #6b7280;
    --azul: #2563eb;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
    margin: 0;
    padding: 32px 16px;
    background: #f6f7f9;
    color: var(--tinta);
  }}
  .contenedor {{
    max-width: 1080px;
    margin: 0 auto;
    background: #ffffff;
    border-radius: 14px;
    padding: 28px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.06);
  }}
  header h1 {{ margin: 0 0 6px; font-size: 24px; letter-spacing: -0.02em; }}
  header h1 .logo {{ color: var(--verde-oscuro); }}
  header p {{ margin: 0 0 22px; color: var(--gris); }}
  table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
  thead th {{
    text-align: left; padding: 12px 14px; background: #f0f2f5;
    color: #374151; font-weight: 600; border-bottom: 2px solid #e5e7eb;
  }}
  tbody td {{ padding: 14px; border-bottom: 1px solid #eef0f3; vertical-align: middle; }}
  tbody tr:hover {{ background: #fafbfc; }}
  .empresa {{ font-weight: 600; }}
  .sub {{ color: var(--gris); font-size: 12px; margin-top: 2px; }}
  .mailto {{ color: var(--gris); text-decoration: none; }}
  .mailto:hover {{ text-decoration: underline; }}
  .estado {{
    display: inline-block; padding: 4px 10px; border-radius: 999px;
    font-size: 11px; font-weight: 600;
  }}
  .estado-pendiente {{ background: #f1f5f9; color: #475569; }}
  .estado-enviado {{ background: #dcfce7; color: #166534; }}
  .badge {{
    display: inline-block; padding: 4px 10px; border-radius: 999px;
    font-size: 12px; font-weight: 600; background: #fff4e5; color: #b45309;
  }}
  .link-web {{ color: var(--azul); text-decoration: none; font-weight: 600; }}
  .link-web:hover {{ text-decoration: underline; }}
  .sin-web {{ color: var(--gris); font-style: italic; }}
  .btn-wa {{
    display: inline-block; background: var(--verde); color: #ffffff;
    text-decoration: none; padding: 9px 16px; border-radius: 8px;
    font-weight: 600; font-size: 13px; white-space: nowrap;
    transition: background .15s ease, transform .05s ease;
  }}
  .btn-wa:hover {{ background: var(--verde-oscuro); }}
  .btn-wa:active {{ transform: translateY(1px); }}
  footer {{ margin-top: 20px; color: var(--gris); font-size: 13px; text-align: center; }}
  @media (max-width: 600px) {{
    .contenedor {{ padding: 16px; }}
    table {{ font-size: 12px; }}
    thead th, tbody td {{ padding: 8px 6px; }}
  }}
</style>
</head>
<body>
  <div class="contenedor">
    <header>
      <h1><span class="logo">Nexora</span> · Prospección B2B Maracaibo</h1>
      <p>Haz clic en "Enviar WhatsApp" para abrir el chat con el mensaje listo.</p>
    </header>
    <table>
      <thead>
        <tr>
          <th>Empresa</th>
          <th>Nicho</th>
          <th>Estado de la web</th>
          <th>Web</th>
          <th>Estado</th>
          <th>Acción</th>
        </tr>
      </thead>
      <tbody>
        {filas}
      </tbody>
    </table>
    <footer>Generado automáticamente por la pipeline de prospección de Nexora.</footer>
  </div>
</body>
</html>
"""

    ruta = Path(archivo)
    ruta.write_text(documento, encoding="utf-8")
    return str(ruta)

# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera la tabla de prospección de Nexora desde prospectos.json."
    )
    parser.add_argument(
        "--json",
        default=ARCHIVO_ENTRADA,
        help=f"Ruta al JSON de prospectos (por defecto: {ARCHIVO_ENTRADA}).",
    )
    parser.add_argument(
        "--nicho",
        default="clinica",
        choices=sorted(NICHOS_VALIDOS) + ["all"],
        help="Filtra por nicho (por defecto: clinica).",
    )
    parser.add_argument(
        "--out",
        default=ARCHIVO_SALIDA,
        help=f"Archivo HTML de salida (por defecto: {ARCHIVO_SALIDA}).",
    )
    args = parser.parse_args()

    nicho_filtro = None if args.nicho == "all" else args.nicho

    try:
        prospectos = cargar_desde_json(args.json, nicho_filtro)
    except (OSError, ValueError, json.JSONDecodeError) as e:
        print(f"[ERROR] No se pudieron cargar los prospectos: {e}", file=sys.stderr)
        return 1

    if not prospectos:
        print("[AVISO] No hay prospectos que coincidan con el filtro.", file=sys.stderr)
        return 1

    print(f"\nNexora · {len(prospectos)} prospectos cargados "
          f"(nicho: {args.nicho}) desde {args.json}.\n")
    print("=" * 78)
    for p in prospectos:
        msg = generar_mensaje(p)
        print(f"\n• {p.nombre}  [{ETIQUETA_NICHO[p.nicho]} · {p.web} · {p.estado_contacto}]")
        print(f"  ({len(msg.split())} palabras) {msg}")
    print("\n" + "=" * 78)

    ruta = generar_html(prospectos, args.out)
    print(f"\n✔ Archivo generado: {ruta}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())