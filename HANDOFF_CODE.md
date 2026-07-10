# Handoff para Claude Code

> **ESTADO 2026-07-10: los 4 pendientes COMPLETADOS por la sesión Code** (+ QA del rediseño
> de chat de Cowork + skills con few-shot). Detalle completo en
> `backend/reports/REPORTE_SESION_CODE_2026-07-10.md`. Claves: Vane solo funciona por
> streaming (stream:false cuelga); OLLAMA_MAX_LOADED_MODELS=2; embeddings unificados en
> bge-m3 (RAG re-ingestado); modo agente en `/agent` con SafetyPolicy y aprobación obligatoria.

Proyecto: Modelo IA Carrera — asistente IA 100% local.
Backend: FastAPI + Ollama + ChromaDB + Vane/Perplexica con fallback SearXNG (`backend/`, puerto 8000).
Frontend: Next.js 16 + TS + Tailwind + shadcn (`frontend/`, correr con `npm run dev -- -p 3001`; el 3000 lo usa Vane).
Modelos Ollama: qwen2.5:7b (general), qwen2.5-coder:7b (código), qwen3-embedding:0.6b + bge-m3 (embeddings), llama3.2 (router).

## Hecho (sesión Cowork 2026-07-08)

1. **UI refinada completa** (18 fases): design tokens, sidebar agrupada, topbar con estados, dashboard, chat con accordion de opciones, skills con playground único, logs de diagnóstico, settings en accordions, agent placeholder. Playwright configurado con 18 screenshots. Ver `frontend/FINAL_UI_REFINEMENT_REPORT.md`.
2. **Vane arreglado en código** (causa raíz: timeout 8s vs búsquedas de 30-120s + detección frágil de provider):
   - `backend/app/infrastructure/web/perplexica_client.py` reescrito (detección robusta, caché providers, last_error, fallback embedding bge-m3).
   - `web_search_service.py`: contrato engine/fallback_used/vane_error; síntesis protegida.
   - `/health`: searxng top-level, web_search.status ok|degraded|error, last_error.
   - `settings.yaml`: vane_search_timeout 60, vane_fallback_embed_model bge-m3.
   - Nuevo `backend/scripts/debug_vane_search.py` (prueba providers+search, timeout 120s).
   - Ver `backend/reports/VANE_AUDIT.md` y `backend/reports/FINAL_VANE_FIX_REPORT.md`.
3. **Skills "entrenadas"**: los 5 system prompts reescritos con reglas concretas (español, admitir incertidumbre, no inventar APIs, stack del usuario, ciber defensiva).
4. **RAG**: ingesta ahora acepta .md/.txt además de PDF; 7 guías curadas nuevas en `C:\Users\angel\Modelo local\RAG` (Asistente/, Programacion/, Cyberseguridad/, Base de Datos/, UI/). Aún NO ingestadas.
5. Tests: 15/15 unitarios en verde (vane client, web search, ingesta md). Todo el backend compila.

## Pendiente (hacer en Code, en orden)

1. QA frontend tras retoques: `cd frontend; npm run lint; npm run build; npm run test:ui` (con dev server en 3001). Fueron 3 cambios chicos: metric-card.tsx, dashboard-view.tsx, top-bar.tsx.
2. Backend en vivo: `cd backend; .\.venv\Scripts\Activate.ps1; .\scripts\test_all.ps1` y `python .\scripts\debug_vane_search.py`. Si search sigue en timeout con 120s: verificar `docker exec vane sh -c "wget -qO- http://host.docker.internal:11434/api/tags"`, OLLAMA_HOST=0.0.0.0, firewall 11434.
3. Ingestar RAG nuevo: POST /ingest con path `C:\Users\angel\Modelo local\RAG` (o por carpeta) y probar consulta "según mis documentos del Asistente...".
4. Parte B pendiente completa: modo agente real (plan largo en conversación previa: SafetyPolicy, workspace read-only, plan, diff, apply con aprobación, comandos whitelisted). NO full-auto, todo con aprobación.

## Reglas del proyecto

No borrar rutas/stores/cliente API ni backend. No cambiar endpoints sin justificar. No full-auto en agente. No APIs de pago, solo Ollama local. SearXNG queda como fallback. Nada avanza si lint/build/tests fallan. Reporte al final de cada bloque.

## Ojo

En la sesión Cowork hubo un bug de escritura que truncaba archivos editados; todo quedó verificado íntegro (ast/py_compile en 0 errores), pero si algo se ve raro, revisar el final del archivo primero.
