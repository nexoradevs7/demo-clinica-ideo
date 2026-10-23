# Nexora · Pipeline Autónoma de Prospección B2B (Multi-Agente)

Sistema autónomo que se ejecuta **todos los días a las 08:00 AM** (hora local de
Venezuela, `America/Caracas`) y orquesta un pipeline de **4 agentes especializados**
para prospectar 3 nichos en Maracaibo:

| Nicho | Segmento |
|-------|----------|
| `mecanica` | Talleres Mecánicos |
| `clinica` | Clínicas y Centros Médicos |
| `ingenieria` | Empresas de Ingeniería y Consultoría Técnica |

---

## 1. Arquitectura

```
                       ┌─────────────────────────────────────────────┐
                       │   DISPARADOR (Scheduler) — 08:00 Caracas     │
                       │   scheduler.py  ·  schedule_create (DSH)     │
                       └───────────────────────┬─────────────────────┘
                                               │ dispara
                                               ▼
   ┌────────────────────────────────────────────────────────────────────────┐
   │                     PIPELINE (cadena estricta)                         │
   │                                                                        │
   │  [1] Scraper  ──►  [2] Ordenador  ──►  [3] Auditor  ──►  [4] QA        │
   │  Buscador          Linter/Cleaner      Auditor Técnico    Supervisor    │
   │  prospectos        HTML/Tailwind       rendimiento        producción    │
   │  + mensajes        + carpetas          SEO + SSL          enlaces/lorem │
   │  + tablero HTML                                         responsive      │
   │                                                                        │
   └────────────────────────────────────────────────────────────────────────┘
                                               │
                                               ▼
                         pipeline_state.json (contrato de datos único)
```

**Dos capas, ambas incluidas:**

1. **Capa determinista (Python)** — `orchestrator.py` + `lib/`. Ejecuta el pipeline
   completo sin depender de un LLM. Es el "motor de verdad" y funciona con cualquier
   scheduler del sistema operativo.
2. **Capa de agentes LLM (DeepSeek Harness)** — los 4 agentes definidos en `agents/`
   usan los módulos de `lib/` como herramientas y añaden criterio (el Scraper puede
   `web_search` nuevos prospectos, el Auditor puede `web_fetch` URLs reales, etc.).

---

## 2. Los 4 agentes (roles, entradas y salidas)

| # | Agente | Entrada | Salida | Herramienta Python |
|---|--------|---------|--------|--------------------|
| 1 | **Buscador/Scraper** | `data/prospectos.json` | `salida/prospeccion_nexora.html` + mensajes | `lib/scraper.py`, `lib/messages.py`, `lib/html_board.py` |
| 2 | **Ordenador de Código** | HTML del paso 1 | reporte `ordenador` + `orden_carpetas` | `lib/linter.py` |
| 3 | **Auditor Técnico** | HTML del paso 1 (+ URL opcional) | reporte `auditor` (perf/SEO/SSL) | `lib/auditor.py` |
| 4 | **Supervisor QA** | HTML + reportes previos | veredicto `listo_para_entregar` | `lib/qa.py` |

Las definiciones completas (objetivo + Definition of Done) están en `agents/*.md`.

---

## 3. Comunicación y paso de datos entre agentes

### 3.1 Contrato de datos único (source of truth)

Todo el sistema comparte **un único documento**: `salida/reportes/pipeline_state.json`
(cuyo esquema formal está en `schemas/pipeline_state.json`).

```jsonc
{
  "run_id": "20261022-002822",
  "timestamp": "2026-10-22T00:28:22",
  "nichos_objetivo": ["mecanica", "clinica", "ingenieria"],
  "total_prospectos": 9,
  "prospectos": [ /* Agente 1: entrada normalizada */ ],
  "mensajes":   [ /* Agente 1: mensaje + enlace_wa por prospecto */ ],
  "tablero_html": "salida/prospeccion_nexora.html",
  "ordenador":  { /* Agente 2 */ },
  "orden_carpetas": { /* Agente 2 */ },
  "auditor":    { /* Agente 3 */ },
  "qa":         { /* Agente 4: listo_para_entregar */ }
}
```

### 3.2 Protocolo de paso (handoff)

Cada agente **lee el contrato, escribe su sección y lo deja listo para el siguiente**:

```
Scraper     ── escribe  prospectos, mensajes, tablero_html ──►
Ordenador   ── lee tablero_html ── escribe  ordenador ───────►
Auditor     ── lee tablero_html ── escribe  auditor ────────►
QA          ── lee tablero_html + reportes ── escribe  qa ──►  veredicto
```

### 3.3 Secuenciación (dos mecanismos equivalentes)

- **Modo determinista**: `orchestrator.py` encadena las funciones en orden estricto.
- **Modo DeepSeek Harness**: el Lead crea tareas en el **tablero compartido** con
  dependencias `blocked_by` para que el orden quede garantizado:

| Tarea | Depende de | `write_scopes` (advisory) |
|-------|-----------|---------------------------|
| T1 Scraper | — | `nexora_pipeline/data`, `nexora_pipeline/salida` |
| T2 Ordenador | T1 | `nexora_pipeline/salida` |
| T3 Auditor | T2 | `nexora_pipeline/salida` |
| T4 QA | T3 | `nexora_pipeline/salida` |

> Regla: los agentes **nunca** se comunican con mensajes informales; se comunican
> escribiendo/leyendo el contrato de datos y actualizando el tablero compartido.

---

## 4. El programador diario (Scheduler)

`scheduler.py` dispara la pipeline a las 08:00 `America/Caracas` (UTC-4, sin
horario de verano). Tres modos:

```bash
# (a) Ejecutar una sola vez ahora (para Task Scheduler / cron)
python scheduler.py --once

# (b) Daemon de larga duración (bucle interno, sin depender del SO)
python scheduler.py --daemon

# (c) Imprimir el comando de registro en Windows Task Scheduler
python scheduler.py --print-schtasks
```

**Opción A — Daemon (recomendada, multiplataforma):**
```bash
cd nexora_pipeline
python scheduler.py --daemon
```
Mantén el proceso vivo (o córrelo como servicio). Calcula el próximo 08:00 Caracas
con `zoneinfo` y espera exactamente hasta esa hora.

**Opción B — Windows Task Scheduler (nativo):**
```bash
python scheduler.py --print-schtasks   # copia el comando que imprime
```
El comando usa `--once`, por lo que Task Scheduler lo invoca cada día a las 08:00.
*Nota:* `schtasks` usa la zona horaria **local** del equipo; si el equipo no está en
`America/Caracas`, ajusta `/ST` a la hora equivalente (08:00 Caracas = 12:00 UTC).

**Opción C — cron (Linux/macOS):**
```bash
crontab -e
# 08:00 Caracas = 12:00 UTC:
0 12 * * * cd /ruta/nexora_pipeline && python3 scheduler.py --once >> logs/pipeline.log 2>&1
```

**Opción D — Disparador nativo de DeepSeek Harness:**
```text
schedule_create({
  title: "Pipeline diaria Nexora",
  prompt: "Ejecuta la pipeline Nexora: despacha a los 4 agentes en orden Scraper → Ordenador → Auditor → QA.",
  daily: { time: "08:00:00", time_zone: "America/Caracas" }
})
```
Este disparador entrega un *prompt* al Lead de la sesión, que a su vez orquesta a
los 4 agentes (ver sección 6).

---

## 5. Cómo iniciar el entorno en la terminal

### Requisitos
- Python 3.9+ (usa `zoneinfo` de la librería estándar; en Windows instala `tzdata`).

### Ejecución rápida (pipeline determinista)

```bash
# 1) Entrar al proyecto
cd nexora_pipeline

# 2) Ejecutar el pipeline una vez (usa data/prospectos.json)
python orchestrator.py

# 3) O con CSV propio
python orchestrator.py --entrada data/prospectos.csv

# 4) Con auditoría remota (URL pública del prototipo)
python orchestrator.py --url https://nexora.com/prototipo

# 5) Dejar el programador diario activo
python scheduler.py --daemon
```

Salidas generadas:
- `salida/prospeccion_nexora.html` — tablero interactivo con botones "Enviar WhatsApp".
- `salida/reportes/pipeline_state.json` — estado completo del pipeline.

---

## 6. Arranque con DeepSeek Harness (modo multi-agente LLM)

### 6.1 Crear el disparador diario
```text
schedule_create({
  title: "Pipeline diaria Nexora",
  prompt: "08:00 — arranca la pipeline Nexora. Crea las tareas encadenadas y despacha a scraper, ordenador, auditor y qa en ese orden.",
  daily: { time: "08:00:00", time_zone: "America/Caracas" }
})
```

### 6.2 Crear los 4 agentes (una sola vez)
```text
spawn_teammate({ name: "scraper",   description: "Buscador/Scraper de prospectos",   prompt: "<contenido de agents/01_scraper.md>" })
spawn_teammate({ name: "ordenador", description: "Ordenador de código (linter)",      prompt: "<contenido de agents/02_ordenador.md>" })
spawn_teammate({ name: "auditor",   description: "Auditor técnico (perf/SEO/SSL)",    prompt: "<contenido de agents/03_auditor.md>" })
spawn_teammate({ name: "qa",        description: "Supervisor de producción (QA)",     prompt: "<contenido de agents/04_qa.md>" })
```

### 6.3 Cada mañana: encadenar las tareas
```text
team_task_create({ subject: "1 Scraper — prospectos y tablero",  description: "Lee data/prospectos.json y genera salida/prospeccion_nexora.html", write_scopes: ["nexora_pipeline/data", "nexora_pipeline/salida"] })
team_task_create({ subject: "2 Ordenador — limpiar HTML/carpetas", blocked_by: ["<id_T1>"], write_scopes: ["nexora_pipeline/salida"] })
team_task_create({ subject: "3 Auditor — perf/SEO/SSL",          blocked_by: ["<id_T2>"], write_scopes: ["nexora_pipeline/salida"] })
team_task_create({ subject: "4 QA — veredicto de entrega",      blocked_by: ["<id_T3>"], write_scopes: ["nexora_pipeline/salida"] })
```

### 6.4 Despachar y monitorear
```text
send_message({ target: "scraper",   message: "Arranca la Etapa 1 (T1)." })
# cuando T1 se complete, el Lead despacha al siguiente:
send_message({ target: "ordenador", message: "Arranca la Etapa 2 (T2)." })
# ... y así sucesivamente hasta que qa reporte listo_para_entregar.
wait_agent({ timeout_ms: 300000 })   # monitorear cambios
```
> Las tareas **no** despiertan solas a su dueño: el Lead debe despachar cada etapa
> con `send_message` cuando sus bloqueos se hayan liberado. Usa `list_agents` /
> `wait_agent` para re-chequear el estado sin hacer polling.

---

## 7. Verificación (testing)

```bash
python orchestrator.py --entrada data/prospectos.json --salida salida
```
Resultado esperado: `VEREDICTO: LISTO PARA ENTREGAR ✅` con 0 enlaces rotos,
sin Lorem Ipsum y responsive `sí`.

Estructura final del repositorio:
```
nexora_pipeline/
├── README.md
├── scheduler.py          # disparador diario 08:00 Caracas
├── orchestrator.py       # coordinador determinista de las 4 etapas
├── lib/                  # herramientas de cada agente
│   ├── messages.py  scraper.py  html_board.py
│   ├── linter.py  auditor.py  qa.py
├── agents/               # definiciones de los agentes (prompts + DoD)
│   ├── 00_coordinador.md  01_scraper.md  02_ordenador.md
│   ├── 03_auditor.md  04_qa.md
├── data/prospectos.json  # entrada diaria (JSON o CSV)
├── schemas/pipeline_state.json  # contrato de datos
└── salida/               # salidas generadas
    ├── prospeccion_nexora.html
    └── reportes/pipeline_state.json
```
