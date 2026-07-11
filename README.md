# Modelo IA Carrera

Plataforma local de IA para estudio y trabajo (Redes, Ciberseguridad, programación, UI/UX,
bases de datos). Todo corre en tu laptop: **Ollama** (modelos), **FastAPI** (backend),
**ChromaDB** (RAG), **Vane/SearXNG** (búsqueda web en Docker) y **Next.js** (UI).
Sin APIs de pago, sin datos fuera de tu máquina.

## Arranque rápido

```powershell
# 1. Servicios (docker + vane + watchdog GPU + backend :8000)
cd "C:\Users\angel\Modelo local\modelo-ia-carrera\backend"
.\scripts\run_all.ps1

# 2. Frontend (:3001)
cd "C:\Users\angel\Modelo local\modelo-ia-carrera\frontend"
npm run dev -- -p 3001
```

Abrir http://localhost:3001 — arranca en modo **pro** (centro de comando); el toggle
"Modo pro" del sidebar cambia a modo **simple** (chat limpio para uso diario).

> AVISO: si las respuestas van lentas, casi seguro Ollama arrancó sin GPU (pasa tras
> suspender la laptop): `cd backend ; .\scripts\check_gpu.ps1 -Fix`

## Qué puede hacer

| Función | Dónde | Cómo funciona |
|---|---|---|
| Chat con skills | `/chat` | Router elige skill (programación/ciber/BD/UI-UX/general) y modelo; streaming token a token; menú `+` para modelo/RAG/colección; globo = búsqueda web |
| RAG local | `/rag` y chat | Tus documentos en ChromaDB (bge-m3); umbral anti-alucinación calibrado; si no hay nada relevante te lo dice |
| Búsqueda web | globo del chat | Vane primero; si no consigue fuentes cae a SearXNG + síntesis local (~1-2 min) |
| Generar documentos | `/documents` | Reportes, manuales, README, API docs, checklists en MD/HTML/DOCX/PDF, con tus fuentes RAG opcionales |
| Modo agente | `/agent` | Le das una carpeta y un objetivo -> plan -> diffs -> TU apruebas cada cambio y comando |
| Diagnóstico | `/logs`, `/models`, dashboard | Logs del backend, modelos Ollama, estado real de servicios |

## Modelos (Ollama)

| Modelo | Uso | Nota |
|---|---|---|
| qwen2.5:7b | chat general, RAG, documentos | ~27 tok/s en GPU (offload parcial) |
| qwen2.5-coder:7b | skills de código y agente | |
| llama3.2 | síntesis de búsqueda web | ~98 tok/s en GPU (entra completo en VRAM) |
| bge-m3 | TODOS los embeddings | compartido para no intercambiar modelos |

Config en `backend/config/settings.yaml`. Env del sistema: `OLLAMA_MAX_LOADED_MODELS=2`.

## Scripts útiles (backend/scripts)

- `run_all.ps1` / `stop_all.ps1` — levantar/parar todo
- `check_all.ps1` — diagnóstico completo (incluye GPU)
- `check_gpu.ps1 [-Fix]` — ¿Ollama está usando la RTX 3060?
- `test_all.ps1` — pytest con cobertura (55 tests)
- `eval_rag.py` — calidad del RAG con 20 preguntas (15 reales + 5 trampa)
- `debug_vane_search.py` — diagnóstico de búsqueda Vane

## Tests

```powershell
cd backend ; .\scripts\test_all.ps1          # 55 backend
cd frontend ; npm run lint ; npm run build
npx playwright test                            # 20 UI (screenshots + interacción)
```

## Documentación

- `PROJECT_STATE.md` — estado real por componente (leer primero)
- `PROJECT_AUDIT_REPORT.md` — auditoría completa con hallazgos y plan
- `DECISIONS.md` / `KNOWN_ERRORS.md` / `CHANGELOG_LOCAL.md` — memoria del proyecto
- `NEXT_AUTOPILOT_TASKS.md` — cola de trabajo pendiente
- `backend/reports/` — reportes técnicos por área

## Reglas del proyecto

Local-first, solo Ollama (sin APIs de pago), SearXNG como fallback de web, el modo agente
JAMÁS ejecuta nada sin aprobación, y nada avanza si lint/build/tests fallan.
