# KNOWN_ERRORS — errores conocidos y su estado

## Activos (con mitigación)

1. **Detección CUDA intermitente de Ollama** — tras suspender/arrancar a veces solo ve la iGPU
   y cae a CPU (todo 4-14× más lento). Mitigado: `backend/scripts/check_gpu.ps1 -Fix` (integrado
   en run_all/check_all). Si persiste: nvidia-smi, driver, `%LOCALAPPDATA%\Ollama\server.log`.
2. **`stream:false` de Vane cuelga para siempre** — bug del fork; el cliente SIEMPRE usa
   streaming. No usar el debug script viejo ni curl con stream false contra /api/search.
3. **Engines de SearXNG se suspenden ~3 min bajo rate-limit** (403/429) — búsquedas repetidas
   dan 0 resultados temporalmente; transitorio, el fallback y el abort temprano lo manejan.
4. **Bug de escritura en sesiones Cowork** — a veces trunca archivos al editar. Mitigado: git +
   verificar el final de archivos tocados por Cowork. (3 archivos afectados el 2026-07-09 y
   schemas.py perdió una edición el 2026-07-10.)
5. **Cola única de Ollama (NUM_PARALLEL=1)** — peticiones abandonadas por timeout siguen
   ejecutándose y bloquean lo siguiente varios minutos. No abandonar requests a lo loco; revisar
   `/api/ps` al diagnosticar lentitud.

## Resueltos (no reintroducir)

- Crash de `/chat` al abrir menú `+`: `DropdownMenuLabel` de Base UI exige `DropdownMenuGroup`
  padre (test de regresión en ui-smoke.spec.ts).
- `/health` siempre "ok": ahora deriva de ollama+chroma+web.
- Timeouts eternos de Vane: eran 3 causas apiladas (MAX_LOADED=1 + stream:false roto + engines
  suspendidos). Ver DECISIONS.md.
- RAG alucinaba con preguntas fuera de los documentos: umbral 1.03 calibrado (eval_rag.py).
- Ingesta re-embebía duplicados: ahora deduplica por hash ANTES de embeber.
- `npm` no ejecutaba en el agente (Windows .cmd): resuelto con shutil.which.
- Colecciones fantasma: query de Chroma ya no crea colecciones inexistentes.
