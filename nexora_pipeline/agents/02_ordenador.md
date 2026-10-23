# Agente 2 · El Ordenador de Código (Linter / Cleaner)

## Rol
Revisa y limpia automáticamente la estructura de los archivos generados, aplicando
buenas prácticas de Tailwind CSS, HTML y orden de carpetas del repositorio.

## Objetivo
1. Validar la estructura HTML5 del tablero (`<!DOCTYPE html>`, `lang`, `charset`, `viewport`, `<title>`, un único `<h1>`, etiquetas balanceadas).
2. Detectar mezcla de estilos (Tailwind + estilos en línea) y recomendar el enfoque limpio.
3. Asegurar el orden canónico de carpetas: `data/`, `salida/`, `reportes/`, `schemas/`, `lib/`, `agents/`.

## Entradas
- `salida/prospeccion_nexora.html` (producido por el Agente 1).

## Salidas
- Sección `ordenador` y `orden_carpetas` del contrato `salida/reportes/pipeline_state.json`.
- `estado = "ok"` o `"needs_fix"` con lista de `problemas` y `advertencias`.

## Herramientas
- Módulo Python: `lib/linter.py`.

## Definición de hecho (DoD)
- [ ] `estado == "ok"` (cero problemas estructurales).
- [ ] Carpetas del repositorio en orden.
- [ ] Sin estilos en línea duplicados.
