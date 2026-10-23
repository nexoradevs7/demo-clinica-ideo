# -*- coding: utf-8 -*-
"""
Agente 1 (Buscador/Scraper) — Tablero HTML interactivo.

Genera una tabla limpia con: empresa (+ teléfono/tipo de contacto), nicho,
estado de la web, enlace a su web real (si existe) y botón verde
"Enviar WhatsApp" con el enlace wa.me ya codificado.
"""

from __future__ import annotations

import html
from pathlib import Path
from typing import Dict, List

from .messages import ETIQUETA_NICHO

# Etiqueta legible para el tipo de contacto.
ETIQUETA_CONTACTO = {
    "directo": "contacto directo",
    "atencion_general": "atención general",
    "no_encontrado": "sin teléfono",
}

# Etiqueta legible para el estado de contacto (mini-CRM).
ETIQUETA_ESTADO = {
    "pendiente": "Pendiente",
    "correo_enviado": "Correo enviado",
    "whatsapp_enviado": "WhatsApp enviado",
    "respondido": "Respondido",
}


def generar_tablero(registros: List[Dict[str, str]], archivo: str) -> str:
    """
    Genera el tablero HTML.

    `registros` es una lista de diccionarios con claves:
        nombre, nicho, web, url, telefono, tipo_contacto, enlace_wa
    Devuelve la ruta del archivo escrito.
    """
    filas: List[str] = []
    for r in registros:
        url = r.get("url", "")
        telefono = r.get("telefono", "")
        email = r.get("email", "")
        tipo = ETIQUETA_CONTACTO.get(r.get("tipo_contacto", "directo"), r.get("tipo_contacto", "directo"))
        estado = r.get("estado_contacto", "pendiente")
        etiqueta_estado = ETIQUETA_ESTADO.get(estado, estado)
        clase_estado = "estado-enviado" if estado != "pendiente" else "estado-pendiente"

        celda_web = (
            f'<a class="link-web" href="{html.escape(url, quote=True)}" '
            'target="_blank" rel="noopener">Ver web</a>'
            if url
            else '<span class="sin-web">Sin web</span>'
        )

        partes = []
        if telefono:
            partes.append(f"{html.escape(telefono)} · {html.escape(tipo)}")
        if email:
            partes.append(
                f'<a class="mailto" href="mailto:{html.escape(email, quote=True)}">'
                f"{html.escape(email)}</a>"
            )
        sublinea = " · ".join(partes) if partes else "sin contacto"

        filas.append(
            "<tr>"
            f"<td><div class='empresa'>{html.escape(r['nombre'])}</div>"
            f"<div class='sub'>{sublinea}</div></td>"
            f"<td>{html.escape(ETIQUETA_NICHO.get(r['nicho'], r['nicho']))}</td>"
            f"<td><span class='badge'>{html.escape(r['web'])}</span></td>"
            f"<td>{celda_web}</td>"
            f"<td><span class='estado {clase_estado}'>{html.escape(etiqueta_estado)}</span></td>"
            f"<td><a class='btn-wa' href='{html.escape(r['enlace_wa'], quote=True)}' "
            "target='_blank' rel='noopener'>Enviar WhatsApp</a></td>"
            "</tr>"
        )
    cuerpo_tabla = "\n        ".join(filas)

    documento = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Tablero de prospección B2B de Nexora para Maracaibo: talleres mecánicos, clínicas y empresas de ingeniería.">
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
  .estado {{ display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 11px; font-weight: 600; }}
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
        {cuerpo_tabla}
      </tbody>
    </table>
    <footer>Generado automáticamente por la pipeline de prospección de Nexora.</footer>
  </div>
</body>
</html>
"""

    ruta = Path(archivo)
    ruta.parent.mkdir(parents=True, exist_ok=True)
    ruta.write_text(documento, encoding="utf-8")
    return str(ruta)
