# -*- coding: utf-8 -*-
"""
Agente 1 (Buscador/Scraper) — Ingesta y normalización de la lista de prospectos.

En la versión determinista, lee la lista desde un JSON (o CSV) y la valida.
En el entorno de agentes de DeepSeek Harness, el Agente 1 puede además usar
web_search / web_fetch para ENRIQUECER la lista (nuevos negocios en Maracaibo)
antes de pasarla por aquí.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import List

from .messages import Prospecto


def cargar_desde_json(ruta: str) -> List[Prospecto]:
    """Lee prospectos desde JSON: lista directa o {"prospectos": [...]}."""
    datos = json.loads(Path(ruta).read_text(encoding="utf-8"))
    if isinstance(datos, dict):
        datos = datos.get("prospectos", [])
    if not isinstance(datos, list):
        raise ValueError(f"El JSON '{ruta}' no contiene una lista de prospectos.")
    obligatorios = ("nombre", "nicho", "telefono")
    opcionales = ("web", "url", "email", "contacto", "tipo_contacto", "fuente",
                  "estado_contacto", "fecha_envio")
    resultado = []
    for item in datos:
        kwargs = {k: item[k] for k in obligatorios if k in item}
        for k in opcionales:
            if k in item and item[k] not in (None, ""):
                kwargs[k] = item[k]
        resultado.append(Prospecto(**kwargs))
    return resultado


def cargar_desde_csv(ruta: str) -> List[Prospecto]:
    """Lee prospectos desde CSV (columnas: nombre,nicho,telefono,web)."""
    prospectos: List[Prospecto] = []
    with open(ruta, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            prospectos.append(
                Prospecto(
                    nombre=fila["nombre"],
                    nicho=fila["nicho"],
                    telefono=fila["telefono"],
                    web=fila.get("web", "Sin Web"),
                )
            )
    return prospectos


def cargar_prospectos(ruta: str) -> List[Prospecto]:
    """Detecta el formato (CSV o JSON) y carga la lista de prospectos."""
    sufijo = Path(ruta).suffix.lower()
    if sufijo == ".csv":
        return cargar_desde_csv(ruta)
    return cargar_desde_json(ruta)
