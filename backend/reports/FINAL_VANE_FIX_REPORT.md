# Final Vane Fix Report

Fecha: 2026-07-08

## Resumen

Se diagnostico y corrigio la integracion con Vane (Perplexica) sin tocar el contenedor: el problema principal era configuracion y robustez del cliente, no el servicio. Ademas se mejoro el fallback SearXNG, el contrato de `/web/search`, el `/health`, la ingesta del RAG (ahora acepta Markdown y TXT) y los system prompts de todas las skills.

## Causa raiz del "Vane no funciona"

1. `vane_search_timeout: 8.0` (antes 1.0): una busqueda Perplexica con qwen2.5:7b local tarda 30-120s. El timeout garantizaba el fallo. **Corregido a 60s.**
2. Deteccion de provider Ollama solo por nombre: si el provider no contiene "ollama"/"11434" en el nombre, fallaba con "no Ollama provider was found". **Ahora detecta por name/id/baseUrl, por presencia del chat model configurado y por forma de tag Ollama de los modelos.**
3. Roundtrip extra a `/api/providers` en cada busqueda. **Ahora hay cache con TTL de 60s.**

## Cambios de codigo

Backend:

- `app/infrastructure/web/perplexica_client.py` — reescrito: deteccion robusta de provider, cache de providers, timeouts separados (providers 10s / search 60s), fallback de embedding a bge-m3, `last_error` observable para /health, logging de provider/modelos/tiempo, `detect_ollama_provider`, `detect_model`, `build_search_payload`, `normalize_response`. Nunca lanza excepcion: error controlado siempre.
- `app/application/services/web_search_service.py` — contrato nuevo: `engine` (vane|searxng|none), `fallback_used`, `vane_error`; `error=None` cuando el fallback responde; sintesis con Ollama protegida (si Ollama falla, devuelve snippets crudos en lugar de tumbar la busqueda); metodo `status()` con ok/degraded/error.
- `app/presentation/endpoints/health.py` — `searxng` top-level y `web_search` con `status`, `fallback_available`, `last_error`. Regla: Vane providers ok pero search fallando = degraded, no error total.
- `app/domain/schemas.py` — `WebSearchResponse.fallback_used/vane_error`; `HealthResponse.searxng`; `ChatResponse.web_engine/web_fallback_used` (para que el chat pueda mostrar el banner de fallback).
- `app/domain/models.py`, `skill_web_search.py`, `chat_service.py` — propagan engine/fallback al chat.
- `app/application/services/ingestion_service.py` — ingesta acepta `.pdf`, `.md` y `.txt` (los md/txt se tratan como pagina 1). Permite alimentar el RAG con guias curadas.
- `config/settings.yaml` + `app/config.py` — `vane_search_timeout: 60`, `vane_fallback_embed_model: bge-m3`, `web_search_fallback: searxng`.
- `scripts/debug_vane_search.py` — nuevo: prueba manual de providers + search con timeout 120s y diagnostico de cada paso.

Skills ("entrenamiento" del asistente):

- Los 5 system prompts (`general`, `programacion`, `ui_ux`, `ciberseguridad`, `bases_datos`) se reescribieron con reglas concretas: responder en espanol, admitir incertidumbre y sugerir modo web/RAG, no inventar URLs/APIs, formato de salida, stack del usuario (FastAPI/Next/Tailwind/shadcn), enfoque defensivo en ciber, EXPLAIN ANALYZE en DB, etc.

Contenido RAG nuevo (`C:\Users\angel\Modelo local\RAG`):

- `Asistente/guia_del_asistente.md` — que es el sistema, modelos, skills, colecciones, limites.
- `Asistente/recetas_de_uso.md` — prompts que funcionan por skill.
- `Programacion/buenas_practicas_desarrollo.md`
- `Programacion/prompting_llms_locales.md` — como promptear 7B y tunear RAG.
- `Cyberseguridad/fundamentos_defensivos.md` — OWASP, hardening, logs, IR.
- `Base de Datos/postgresql_guia_practica.md`
- `UI/principios_ui_ux_resumen.md`

## Pruebas

Tests unitarios (15/15 en verde, ejecutados con harness de stubs sin red):

- `tests/test_vane_client.py` — 7 tests: deteccion de provider (3 vias), fallback embedding, cache de providers, normalizacion, timeout controlado.
- `tests/test_web_search.py` — 5 tests: vane ok, fallback por timeout, fallback sobrevive fallo de Ollama, fallo total controlado ("No web engine available"), error controlado.
- `tests/test_ingestion_markdown.py` — 3 tests nuevos: ingesta de .md, descubrimiento .md/.txt, inferencia de coleccion por carpeta.

Validacion pendiente en tu maquina (requiere servicios vivos):

```powershell
cd "C:\Users\angel\Modelo local\modelo-ia-carrera\backend"
.\.venv\Scripts\Activate.ps1
.\scripts\test_all.ps1
python .\scripts\debug_vane_search.py          # prueba Vane end-to-end
Invoke-RestMethod http://127.0.0.1:8000/health  # ver status/degraded/last_error
```

Para ingestar el contenido nuevo del RAG (desde la UI /documents o):

```powershell
Invoke-RestMethod -Method Post http://127.0.0.1:8000/ingest -ContentType "application/json" -Body '{"path": "C:\\Users\\angel\\Modelo local\\RAG\\Asistente"}'
```

(repetir por carpeta, o sin path para ingestar todo el arbol RAG)

## Compatibilidad

- Ningun endpoint eliminado ni renombrado; todos los campos nuevos son aditivos.
- El frontend existente sigue funcionando: `web_search.search_endpoint` y `providers_endpoint` se conservan.
- Los tests originales se mantienen y pasan.

## Pendientes reales

1. Correr `test_all.ps1` e integracion en tu maquina (aqui no hay acceso a tus servicios).
2. Si `debug_vane_search.py` sigue dando timeout con 120s: el cuello es Vane→Ollama; revisar `docker exec vane sh -c "wget -qO- http://host.docker.internal:11434/api/tags"`, `OLLAMA_HOST=0.0.0.0` y firewall del 11434.
3. Ingestar las guias nuevas del RAG y probar: "Segun mis documentos del Asistente, ¿que modos tiene el sistema?"
4. Parte B (modo agente real) sigue pendiente por diseno.
