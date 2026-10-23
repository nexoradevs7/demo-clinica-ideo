# -*- coding: utf-8 -*-
"""
Agente 4 (Supervisor de Producción / QA final).

Valida que NO existan enlaces rotos, textos de relleno (Lorem Ipsum) ni
fallos responsivos antes de marcar un proyecto/propuesta como
"Listo para entregar al cliente".
"""

from __future__ import annotations

import re
import urllib.request
from pathlib import Path
from typing import Dict, List

_PATRON_LOREM = re.compile(r"lorem\s+ipsum|dolor\s+sit\s+amet", re.IGNORECASE)


def _extraer_enlaces(texto: str) -> List[str]:
    return re.findall(r'(?:href|src)="([^"]+)"', texto)


def _verificar_enlaces(ruta_html: str, verificar_externos: bool = False) -> Dict:
    """Clasifica los enlaces y detecta rotos (internos y, opcionalmente, externos)."""
    texto = Path(ruta_html).read_text(encoding="utf-8")
    base = Path(ruta_html).parent

    internos: List[str] = []
    externos: List[str] = []
    anclas: List[str] = []
    correos: List[str] = []
    for enlace in _extraer_enlaces(texto):
        if enlace.startswith("#"):
            anclas.append(enlace)
        elif enlace.startswith(("http://", "https://")):
            externos.append(enlace)
        elif enlace.startswith(("mailto:", "tel:")):
            correos.append(enlace)
        else:
            internos.append(enlace)

    rotos: List[str] = []

    # Enlaces internos: deben existir en el sistema de archivos.
    for enlace in internos:
        destino = (base / enlace).resolve()
        if not destino.exists():
            rotos.append(enlace)

    # Enlaces externos: verificación opcional para no depender de la red.
    if verificar_externos:
        for enlace in externos:
            try:
                req = urllib.request.Request(enlace, method="HEAD")
                with urllib.request.urlopen(req, timeout=8) as resp:
                    if resp.status >= 400:
                        rotos.append(f"{enlace} (HTTP {resp.status})")
            except Exception as e:  # noqa: BLE001
                rotos.append(f"{enlace} ({e})")

    return {
        "total": len(internos) + len(externos) + len(anclas) + len(correos),
        "internos": internos,
        "externos": externos,
        "anclas": anclas,
        "correos": correos,
        "enlaces_rotos": rotos,
        "sin_enlaces_rotos": not rotos,
    }


def auditar_qa(ruta_html: str, verificar_externos: bool = False) -> Dict:
    """Reporte QA final con el veredicto 'listo_para_entregar'."""
    texto = Path(ruta_html).read_text(encoding="utf-8")

    enlaces = _verificar_enlaces(ruta_html, verificar_externos=verificar_externos)
    lorem = bool(_PATRON_LOREM.search(texto))
    responsive = ('name="viewport"' in texto) and ("@media" in texto)

    bloqueos: List[str] = []
    if enlaces["enlaces_rotos"]:
        bloqueos.append(f"Enlaces rotos: {enlaces['enlaces_rotos']}")
    if lorem:
        bloqueos.append("Se detectó texto de relleno (Lorem Ipsum)")
    if not responsive:
        bloqueos.append("Falta diseño responsivo (viewport / @media)")

    return {
        "enlaces": enlaces,
        "lorem_ipsum_detectado": lorem,
        "responsive": responsive,
        "bloqueos": bloqueos,
        "listo_para_entregar": not bloqueos,
    }
