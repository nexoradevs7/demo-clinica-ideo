# -*- coding: utf-8 -*-
"""
Nexora · Prospección B2B — Maracaibo
Lee prospectos.json, filtra por nicho (por defecto: clinica)
y genera un HTML con botones de WhatsApp.
"""

import argparse
import html
import json
import sys
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

NICHOS_VALIDOS = {"mecanica", "clinica", "ingenieria"}
ETIQUETA_NICHO = {"mecanica": "Mecánica", "clinica": "Clínica", "ingenieria": "Ingeniería"}
ESTADOS_WEB_VALIDOS = {"Sin Web", "Web Lenta", "No Móvil", "Con Web"}
ARCHIVO_ENTRADA = "prospectos.json"
ARCHIVO_SALIDA = "prospeccion_nexora.html"

OFERTA = ("Le armo una vista previa gratuita de su web optimizada "
          "en 24 horas, sin compromiso.")

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

    def __post_init__(self):
        self.nombre = (self.nombre or "").strip()
        self.nicho = (self.nicho or "").strip().lower()
        self.web = (self.web or "Sin Web").strip()
        if self.nicho not in NICHOS_VALIDOS:
            raise ValueError(f"Nicho inválido para '{self.nombre}': {self.nicho!r}")
        if self.web not in ESTADOS_WEB_VALIDOS:
            self.web = "Sin Web"