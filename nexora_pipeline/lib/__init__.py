# -*- coding: utf-8 -*-
"""Paquete de herramientas deterministas de la pipeline de prospección Nexora.

Cada módulo implementa la parte mecánica de uno de los agentes del sistema:
  - scraper.py    -> Agente 1 (Buscador/Scraper): ingesta y normalización.
  - messages.py   -> Agente 1: mensajes personalizados y enlaces wa.me.
  - html_board.py -> Agente 1: tablero HTML interactivo.
  - linter.py     -> Agente 2 (Ordenador de Código): limpieza HTML/Tailwind.
  - auditor.py    -> Agente 3 (Auditor Técnico): rendimiento, SEO, SSL.
  - qa.py         -> Agente 4 (Supervisor/QA final): enlaces rotos, relleno, responsive.
"""
