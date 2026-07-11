# FINAL_BACKEND_REPORT

Estado: 🟢 estable. 57 tests + 1 skip, cobertura ~82%. Clean architecture real.

## Endpoints (9 routers)
- `/chat`, `/chat/stream` (NDJSON) — chat con router de skills
- `/health` — status real (ok/degraded/error) derivado de ollama+chroma+web
- `/models` — lista de modelos Ollama
- `/ingest` — ingesta a ChromaDB (dedup por hash antes de embeber)
- `/rag/collections`, `/rag/query` — RAG con umbral anti-alucinación
- `/web/search` — Vane + fallback SearXNG
- `/logs` — últimas N líneas del log
- `/agent/*` — modo agente (sesiones, plan, diff, apply, revert, file)
- `/documents/*` — generar/descargar/listar documentos

## Calidad
- Errores: handler global → 500 JSON; SafetyViolation → 403; ValueError → 422; KeyError → 404.
- Timeouts: `ollama_timeout=300` (prompts largos en CPU), `vane_search_timeout=180`,
  searxng 15s, providers 10s.
- Logs: loguru con rotación 5MB, retención 5; una línea por request de chat con métricas.
- Config: settings.yaml + env override (pydantic-settings). Todo documentado con comentarios.

## Cambios de esta sesión
- `/chat/stream` nuevo (streaming token a token).
- `/documents/*` nuevo (skill de documentos).
- Agente: shutil.which (npm en Windows), secretos bloqueados, backups+actions.log+persist.
- keep_alive 30m/60m (antes descargaba modelo tras cada request).
- health real; chroma query sin crear colecciones fantasma.

## Pendiente menor
- Singletons con lru_cache para clientes (hoy se construyen por request; Chroma es el caro).
- Sesiones del agente en memoria (persist_state ya deja snapshot en disco; falta reload al arrancar).
- Endpoints /agent/git/* y /agent/index (fase agente PRO).
