# -*- coding: utf-8 -*-
"""
Agente 2 (Ordenador de Código / Linter-Cleaner).

Revisa y reporta la estructura de los archivos generados aplicando buenas
prácticas de HTML5 y Tailwind CSS, y mantiene el orden de carpetas del
repositorio.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, List


def _contenido(ruta: str) -> str:
    return Path(ruta).read_text(encoding="utf-8")


def analizar_html(ruta: str) -> Dict:
    """Valida la estructura del HTML y devuelve un reporte de limpieza."""
    texto = _contenido(ruta)
    problemas: List[str] = []
    advertencias: List[str] = []

    # --- Estructura básica HTML5 ---
    if "<!DOCTYPE html>" not in texto:
        problemas.append("Falta <!DOCTYPE html>")
    if 'lang="es"' not in texto:
        problemas.append('Falta el atributo lang="es"')
    if 'charset="UTF-8"' not in texto and "charset=utf-8" not in texto:
        problemas.append('Falta <meta charset="UTF-8">')
    if 'name="viewport"' not in texto:
        problemas.append('Falta <meta name="viewport">')
    if not re.search(r"<title>.+?</title>", texto, re.S):
        problemas.append("Falta <title>")
    if len(re.findall(r"<h1[ >]", texto)) != 1:
        problemas.append("Debe existir exactamente un <h1> por página")

    # --- Etiquetas balanceadas (principales contenedores) ---
    for etiqueta in ("table", "thead", "tbody", "div", "header", "footer"):
        abiertas = len(re.findall(rf"<{etiqueta}[ >]", texto))
        cerradas = len(re.findall(rf"</{etiqueta}>", texto))
        if abiertas != cerradas:
            problemas.append(
                f"Etiquetas <{etiqueta}> desbalanceadas ({abiertas} abren / {cerradas} cierran)"
            )

    # --- Buenas prácticas Tailwind / CSS ---
    usa_tailwind = "cdn.tailwindcss.com" in texto
    if usa_tailwind and texto.count('style="') > 3:
        advertencias.append("Mezcla Tailwind con estilos en línea; preferir clases utilitarias")
    if not usa_tailwind:
        advertencias.append(
            "No usa Tailwind (hoja CSS dedicada). Es válido; si migras a Tailwind, "
            "elimina la CSS duplicada."
        )

    # --- Consistencia de indentación ---
    if "\t" in texto and "  " in texto:
        advertencias.append("Indentación mixta (espacios y tabuladores)")

    estado = "ok" if not problemas else "needs_fix"
    return {
        "estado": estado,
        "archivo": Path(ruta).name,
        "usa_tailwind": usa_tailwind,
        "problemas": problemas,
        "advertencias": advertencias,
    }


def ordenar_carpetas(base: str) -> Dict:
    """Crea/valida la estructura canónica de carpetas del repositorio."""
    base = Path(base)
    carpetas = ["data", "salida", "reportes", "schemas", "lib", "agents"]
    creadas: List[str] = []
    for c in carpetas:
        destino = base / c
        if not destino.exists():
            destino.mkdir(parents=True, exist_ok=True)
            creadas.append(str(destino.relative_to(base)))
    return {
        "raiz": str(base),
        "carpetas_esperadas": carpetas,
        "creadas_ahora": creadas,
    }
