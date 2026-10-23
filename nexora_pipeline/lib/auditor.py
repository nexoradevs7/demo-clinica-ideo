# -*- coding: utf-8 -*-
"""
Agente 3 (Auditor Técnico).

Corre pruebas automatizadas de rendimiento (peso / tiempo de carga),
etiquetas SEO básicas y seguridad (SSL) sobre la página prototipo.
"""

from __future__ import annotations

import re
import ssl
import time
import urllib.request
from pathlib import Path
from typing import Dict, Optional


def _peso(ruta: str) -> int:
    return Path(ruta).stat().st_size


def _etiquetas_seo(texto: str) -> Dict:
    """Revisa las etiquetas SEO fundamentales de la página."""
    titulo = re.search(r"<title>(.*?)</title>", texto, re.S)
    descripcion = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', texto, re.S)

    titulo_texto = titulo.group(1).strip() if titulo else ""
    descripcion_texto = descripcion.group(1) if descripcion else ""

    return {
        "titulo": titulo_texto,
        "titulo_ok": 10 <= len(titulo_texto) <= 65,
        "meta_description": bool(descripcion_texto),
        "meta_description_ok": 50 <= len(descripcion_texto) <= 160,
        "viewport": 'name="viewport"' in texto,
        "lang_es": 'lang="es"' in texto,
        "un_solo_h1": len(re.findall(r"<h1[ >]", texto)) == 1,
        "imagenes_con_alt": texto.count("alt="),
    }


def _rendimiento_local(ruta: str) -> Dict:
    peso = _peso(ruta)
    # Umbral orientativo: un prototipo < 150 KB se considera liviano.
    return {
        "peso_bytes": peso,
        "peso_kb": round(peso / 1024, 2),
        "estado": "ok" if peso < 150_000 else "revisar (peso alto)",
    }


def _rendimiento_remoto(url: str) -> Dict:
    """Mide el tiempo de carga de una URL pública (si existe)."""
    inicio = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            estado_http = resp.status
            datos = resp.read()
        segundos = round(time.perf_counter() - inicio, 3)
        return {
            "url": url,
            "http_status": estado_http,
            "tiempo_seg": segundos,
            "peso_bytes": len(datos),
            "estado": "ok" if segundos < 3 else "lento (>3s)",
        }
    except Exception as e:  # noqa: BLE001
        return {"url": url, "error": str(e), "estado": "error"}


def _chequeo_ssl(url: str) -> Dict:
    """Verifica que la URL use HTTPS y valida el certificado (básico)."""
    if not url.startswith("https://"):
        return {"estado": "sin_ssl", "detalle": "La URL no usa https (SSL ausente)."}
    try:
        host_port = url.split("://")[1].split("/")[0]
        hostname = host_port.split(":")[0]
        puerto = int(host_port.split(":")[1]) if ":" in host_port else 443
        ssl.get_server_certificate((hostname, puerto), timeout=10)
        return {"estado": "ok", "detalle": f"Certificado SSL válido para {hostname}:{puerto}."}
    except Exception as e:  # noqa: BLE001
        return {"estado": "error", "detalle": f"No se pudo validar el certificado: {e}"}


def auditar(ruta_html: str, url: Optional[str] = None) -> Dict:
    """Consolida el reporte técnico del prototipo (local + opcional remoto)."""
    texto = Path(ruta_html).read_text(encoding="utf-8")
    return {
        "archivo": Path(ruta_html).name,
        "rendimiento_local": _rendimiento_local(ruta_html),
        "seo": _etiquetas_seo(texto),
        "rendimiento_remoto": _rendimiento_remoto(url)
        if url
        else {"estado": "n/a (prototipo local, sin URL pública)"},
        "ssl": _chequeo_ssl(url) if url else {"estado": "n/a (sin URL pública)"},
    }
