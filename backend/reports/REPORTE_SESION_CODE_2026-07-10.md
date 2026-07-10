# Reporte sesión Code — 2026-07-09/10

Cobertura: los 4 pendientes del HANDOFF_CODE.md + QA del rediseño de chat (Cowork) + mejora de la IA.

## 1. QA frontend ✅

`lint` ✅ · `build` ✅ (Next 16, 12 rutas) · `test:ui` **18/18** ✅. Los fallos iniciales eran solo
`ERR_CONNECTION_REFUSED` porque el backend estaba apagado; con backend arriba todo verde.
Screenshots regenerados en `frontend/test-results/ui-screenshots/`.

## 2. Backend en vivo + Vane ✅ (causas raíz encontradas)

`test_all.ps1`: 34→46 tests ✅ (12 nuevos del agente). Diagnóstico de los timeouts de Vane —
eran **tres** problemas apilados:

1. **`OLLAMA_MAX_LOADED_MODELS=1`** (env de usuario): cada búsqueda (chat→embed→chat) forzaba
   2+ recargas de modelo; bajo presión de RAM cada carga tarda 60-160s. **Fix**: subido a `2` y
   pares de modelos que caben juntos: Vane usa `llama3.2` (2GB) + `bge-m3` (1.2GB); chat/RAG usa
   `qwen2.5:7b` + `bge-m3`. Embeddings unificados en **bge-m3 para todo** (RAG re-ingestado).
   Nota: se probó `3` y provoca swapping — 2 es el punto dulce en 16GB.
2. **El modo no-streaming de Vane está roto** (`stream:false` nunca responde, verificado contra el
   código del fork). **Fix**: `perplexica_client.py` ahora consume el stream NDJSON
   (init/sources/response/done). `debug_vane_search.py` actualizado igual.
3. **Engines de SearXNG suspendidos** por rate-limit (403/429, suspensión ~3 min) → 0 resultados →
   Vane alucina respuesta sin fuentes. El servicio la descarta (exige answer+sources) y cae al
   fallback SearXNG+síntesis, que **funciona end-to-end**: probado con "OWASP Top 10 2025" →
   respuesta correcta en español con 5 fuentes reales (owasp.org) en ~4 min.

Extra: `ollama_timeout` configurable (300s) porque 120s cortaba prompts largos de RAG en CPU.

## 3. RAG ingestado ✅

Las 7 guías curadas (.md) + 5 PDFs de UI re-embebidos con bge-m3. Colecciones: `asistente`,
`programacion`, `bases_datos`, `ciberseguridad`, `ui_ux`. Consulta probada:
"según mis documentos del Asistente..." → respuesta correcta citando `guia_del_asistente.md` y
`recetas_de_uso.md`. Los PDFs gigantes (refman MySQL, JLS…) NO se ingestan a propósito: serían
horas de embeddings en CPU; se pueden ingestar por archivo cuando se necesiten.

## 4. Parte B: modo agente ✅ (con aprobación, nunca full-auto)

Backend nuevo `app/application/agent/`:
- **SafetyPolicy**: workspace confinado a `agent_workspace_base`, rutas resueltas contra traversal,
  dirs excluidos (.git, node_modules…), solo extensiones de texto editables, whitelist de comandos
  (git status/diff/log, pytest, npm lint/build/test, pip list) sin metacaracteres de shell,
  ejecución sin shell y con timeout.
- **AgentService**: sesiones → plan (LLM coder, JSON validado paso a paso) → propose diff
  (unified diff, NO escribe) → `apply` solo con `approved:true` (403 si no) → revert disponible.
  Comandos fuera de whitelist quedan `rejected` automáticamente.
- Endpoints `/agent/*` + schemas + **12 tests** nuevos (traversal, whitelist, aprobación
  obligatoria, revert, árbol acotado).
- Frontend `/agent` funcional (reemplaza el placeholder): abrir workspace → objetivo → plan →
  diff coloreado → Aprobar/Rechazar/Revertir → output de comandos → log de actividad.
- **Verificado en vivo** con `C:\Users\angel\Modelo local\agent-demo`: plan real con
  qwen2.5-coder, diff correcto, apply sin aprobación → 403 y archivo intacto, apply aprobado →
  cambio aplicado.

## 5. QA rediseño chat (Cowork) ✅

Los 5 archivos íntegros (sin truncados). `lint` ✅ `build` ✅ `test:ui` 18/18 ✅, screenshots
regenerados — el composer estilo Ollama renderiza bien (pill, `+`, globo, skill selector, flecha).
`ChatRequest.model` respetado en `chat_service.py:40`. Nada que corregir.

## 6. "Entrenamiento" de la IA ✅

Fine-tuning real (LoRA) no es viable en esta laptop (CPU-only, 16GB). Lo que sí mueve la aguja
en modelos 7B locales, aplicado:
- **Few-shot en skills**: `base_skill.py` soporta ejemplos (pregunta→respuesta ideal) y
  `chat_options` por skill. Programación y chat general traen un ejemplo que fija el formato
  (respuesta directa → código con ruta → cómo correr → supuestos). Verificado en vivo: la
  respuesta sigue el formato exacto.
- **Parámetros por skill**: programación/BD/ciber a temperature 0.15 (precisión), UI/UX 0.4
  (creatividad), `repeat_penalty 1.1` (anti-bucles de 7B), `num_ctx 8192` donde el código lo pide.
- **RAG curado** ya ingestado (punto 3) + guía `prompting_llms_locales.md` disponible.

## Config que cambió (resumen)

| Qué | Antes | Ahora |
|---|---|---|
| `OLLAMA_MAX_LOADED_MODELS` (env usuario) | 1 | 2 |
| `vane_chat_model` | qwen2.5:7b | llama3.2:latest |
| `vane_embed_model` | qwen3-embedding:0.6b | bge-m3 |
| `ollama_embed_model` (RAG) | qwen3-embedding:0.6b | bge-m3 |
| `vane_search_timeout` | 60 | 180 |
| `ollama_timeout` (nuevo) | 120 hardcoded | 300 configurable |

## Estado final

Backend 46/46 tests ✅ · Frontend lint+build+18/18 UI ✅ · `/health` todo verde ·
RAG, búsqueda web (con fallback) y modo agente verificados en vivo.

Pendientes sugeridos: ingestar PDFs grandes por lotes cuando se necesiten; persistir sesiones
del agente (hoy en memoria); considerar quitar el paso Vane cuando su SearXNG interno esté sin
resultados (hoy cuesta ~2 min antes del fallback).
