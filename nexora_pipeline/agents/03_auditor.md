# Agente 3 · El Auditor Técnico

## Rol
Corre pruebas automatizadas de rendimiento, tiempos de carga, etiquetas SEO básicas
y seguridad (SSL) sobre las páginas de prototipos generadas.

## Objetivo
1. **Rendimiento local**: peso del archivo HTML (umbral orientativo < 150 KB).
2. **Rendimiento remoto** (si existe URL pública): tiempo de carga y estado HTTP (umbral < 3 s).
3. **SEO básico**: `<title>` (10–65 caracteres), `<meta name="description">` (50–160), `viewport`, `lang="es"`, un único `<h1>`, `alt` en imágenes.
4. **Seguridad SSL**: verificar que la URL pública use `https` y validar el certificado.

## Entradas
- `salida/prospeccion_nexora.html` (ya limpiado por el Agente 2).
- URL pública opcional del prototipo (parámetro `--url`).

## Salidas
- Sección `auditor` del contrato `salida/reportes/pipeline_state.json`.

## Herramientas
- Módulo Python: `lib/auditor.py`.
- En DeepSeek Harness: `web_fetch` para auditorías remotas adicionales.

## Definición de hecho (DoD)
- [ ] Peso local dentro del umbral.
- [ ] Título y meta descripción presentes y con longitud válida.
- [ ] SSL reportado (si aplica URL pública).
