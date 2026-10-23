# -*- coding: utf-8 -*-
"""
Agente 1 (Buscador/Scraper) — Lógica de mensajes personalizados por nicho.

Genera un mensaje de WhatsApp corto (máx. ~50 palabras) ultra enfocado en el
dolor del sector, más la propuesta irresistible, y construye el enlace wa.me
ya codificado.
"""

from __future__ import annotations

import urllib.parse
from dataclasses import dataclass

# Nichos válidos (minúsculas, sin tildes) y su etiqueta legible.
NICHOS_VALIDOS = {"mecanica", "clinica", "ingenieria"}
ETIQUETA_NICHO = {
    "mecanica": "Mecánica",
    "clinica": "Clínica",
    "ingenieria": "Ingeniería",
}
ESTADOS_WEB_VALIDOS = {"Sin Web", "Web Lenta", "No Móvil", "Con Web"}

# Propuesta irresistible incluida en TODOS los mensajes.
OFERTA = (
    "Le armo una vista previa gratuita de su web optimizada "
    "en 24 horas, sin compromiso."
)


@dataclass
class Prospecto:
    """Representa un negocio a prospectar."""

    nombre: str          # Nombre del negocio
    nicho: str           # "mecanica" | "clinica" | "ingenieria"
    telefono: str        # WhatsApp en formato internacional, ej. +58 414 123 4567
    web: str = "Sin Web" # "Sin Web" | "Web Lenta" | "No Móvil" | "Con Web"
    url: str = ""        # Web real del negocio (vacía si no tiene)
    email: str = ""      # Correo de contacto (vacío si no se conoce)
    contacto: str = ""   # Nombre/rol del contacto directo (vacío si no se conoce)
    tipo_contacto: str = "directo"  # directo | atencion_general | no_encontrado
    fuente: str = ""     # URL de la fuente de donde salió el dato
    estado_contacto: str = "pendiente"  # pendiente | correo_enviado | whatsapp_enviado | respondido
    fecha_envio: str = ""               # fecha del último contacto enviado (YYYY-MM-DD)

    def __post_init__(self) -> None:
        self.nombre = self.nombre.strip()
        self.nicho = self.nicho.strip().lower()
        self.web = self.web.strip()
        # Campos de contacto: normalizar cadenas y tolerar valores nulos.
        self.url = (self.url or "").strip()
        self.email = (self.email or "").strip()
        self.contacto = (self.contacto or "").strip()
        self.fuente = (self.fuente or "").strip()
        self.tipo_contacto = (self.tipo_contacto or "directo").strip().lower()
        self.estado_contacto = (self.estado_contacto or "pendiente").strip().lower()
        self.fecha_envio = (self.fecha_envio or "").strip()
        if self.nicho not in NICHOS_VALIDOS:
            raise ValueError(
                f"Nicho inválido para '{self.nombre}': {self.nicho!r}. "
                f"Usa uno de {sorted(NICHOS_VALIDOS)}."
            )
        if self.web not in ESTADOS_WEB_VALIDOS:
            raise ValueError(
                f"Estado de web inválido para '{self.nombre}': {self.web!r}. "
                f"Usa uno de {sorted(ESTADOS_WEB_VALIDOS)}."
            )


def normalizar_numero(telefono: str) -> str:
    """Convierte a formato wa.me: solo dígitos (sin '+', espacios ni guiones)."""
    digitos = "".join(ch for ch in telefono if ch.isdigit())
    if not digitos:
        raise ValueError(f"El teléfono '{telefono}' no contiene dígitos.")
    return digitos


def generar_mensaje(p: Prospecto) -> str:
    """Mensaje enfocado en el dolor del nicho + oferta irresistible."""
    # Evita doble punto si el nombre termina en "." (p. ej. "C.A.").
    nombre = p.nombre.rstrip(". ").strip()

    if p.nicho == "mecanica":
        return (
            f"Hola, {nombre}. Muchos clientes buscan repuestos o auxilio "
            "vial desde el teléfono y hoy no lo encuentran a usted. "
            f"{OFERTA} ¿Se la envío por aquí?"
        )
    if p.nicho == "clinica":
        return (
            f"Hola, {nombre}. La confianza de un paciente se decide en "
            "segundos desde el móvil. Si agendar una cita no es rápido "
            f"y fácil, lo pierden. {OFERTA} ¿Se la envío por aquí?"
        )
    # ingenieria
    return (
        f"Hola, {nombre}. Sus proyectos hablan por usted, pero sin una "
        "web moderna no proyecta la autoridad técnica que merece. "
        f"{OFERTA} ¿Se la envío por aquí?"
    )


def generar_enlace_whatsapp(telefono: str, mensaje: str) -> str:
    """Enlace directo: https://wa.me/<NUMERO>?text=<MENSAJE_URL_ENCODED>."""
    numero = normalizar_numero(telefono)
    return f"https://wa.me/{numero}?text={urllib.parse.quote(mensaje)}"
