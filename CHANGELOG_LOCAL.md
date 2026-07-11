# CHANGELOG_LOCAL

## 2026-07-10 — Sesión autopilot (Claude Code)

### Rendimiento
- **GPU**: descubierto que la RTX 3060 existe y Ollama la ignoraba tras ciertos arranques
  (7 vs 98 tok/s). Watchdog `backend/scripts/check_gpu.ps1` (+integrado en run_all/check_all).
- **keep_alive**: el cliente Ollama enviaba `keep_alive: 0` (descargaba el modelo tras CADA
  petición). Ahora 30m chat / 60m embeddings.
- **Vane**: cliente reescrito a streaming NDJSON (el modo no-streaming del fork cuelga);
  abort temprano cuando no hay fuentes. Búsqueda web: de ~4 min a ~1:15.
- Ingesta RAG: dedup por hash ANTES de embeber (re-ingestar ya no paga embeddings).

### Funcionalidad nueva
- **Streaming de chat**: `POST /chat/stream` (NDJSON meta→delta→sources→done) + UI token a
  token con cursor.
- **Modo agente** (`/agent`): SafetyPolicy (workspace confinado, whitelist de comandos,
  secretos bloqueados) + plan LLM → diff → apply solo con aprobación + revert. UI completa.
- **Skill de documentos** (`/documents`): genera reporte técnico, manuales, README, API docs,
  requerimientos, políticas y checklists en MD/HTML/DOCX/PDF, con RAG opcional, preview,
  historial y descarga.
- **UI simple/pro**: toggle persistente en sidebar; simple = chat limpio tipo Ollama
  (3 rutas), pro = centro de comando (9 rutas); mobile arranca en simple. Motion moderado.
- **RAG anti-alucinación**: umbral `rag_max_distance=1.03` calibrado en vivo;
  `scripts/eval_rag.py` con dataset de 20 preguntas (15 reales + 5 trampa): 20/20.
- Skills con few-shot + parámetros por skill (temperature/num_ctx/repeat_penalty).

### Fixes
- Crash del menú `+` del chat (DropdownMenuLabel sin Group) + test de regresión interactivo.
- `/health` reportaba "ok" siempre; ahora ok/degraded/error real.
- `npm` no ejecutaba en el agente en Windows (shutil.which).
- Chroma ya no crea colecciones fantasma al consultar.
- Toast de fallback web usaba heurística rota; ahora usa `web_fallback_used` del backend.
- Historial de chat persiste (zustand persist, últimos 100 mensajes).

### Infra
- `git init` + baseline (2026-07-10). `.gitignore` para venv/node_modules/chroma/logs/secretos.
- Deps nuevas: motion (frontend); python-docx, reportlab, markdown (backend).
- Tests: backend 34→55; Playwright 18→20 (+ test interactivo de menús).
