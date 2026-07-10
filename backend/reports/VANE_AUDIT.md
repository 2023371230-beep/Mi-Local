# Vane Audit

Fecha: 2026-07-08

## Contexto

Auditoria estatica de codigo + logs del backend. Los checks en vivo (docker, puertos) requieren la maquina local; los comandos exactos estan al final.

## Evidencia de los logs (`backend/logs`)

- `Vane search timed out after 1 seconds.` × ~20 ocurrencias (config antigua con timeout 1s)
- `Vane search timed out after 45.0 seconds.` × 2 (timeout 45s tampoco alcanzo)
- `Vane providers request failed: [WinError 10061]` — contenedor apagado en ese momento
- `Vane is available but no Ollama provider was found.` — providers respondio pero la deteccion fallo

## Diagnostico

1. **Timeout de search demasiado corto.** `vane_search_timeout: 8.0` en settings. Una busqueda de Perplexica con Ollama local (qwen2.5:7b) hace: reformular query + embeddings + fetch de resultados + sintesis LLM. Eso tarda 30-120s en hardware local. Con 8s (y antes 1s) el timeout es garantizado, por eso siempre cae a SearXNG. Vane "no funciona" principalmente por configuracion, no por bug del contenedor.
2. **Deteccion de provider fragil.** `find_ollama_provider` solo matchea `name` contra "ollama"/"11434"/"host.docker.internal". Si el provider en Vane se llama distinto (p.ej. "Local"), falla con "no Ollama provider was found" aunque exista. Falta buscar por `id`, `baseUrl` y por la forma de los modelos (tags tipo `modelo:tag`).
3. **Sin cache de providers.** Cada search hace un roundtrip extra a `/api/providers`, sumando latencia al presupuesto del timeout.
4. **Contrato incompleto.** `/web/search` no expone `fallback_used` ni `vane_error`; cuando el fallback funciona, `error` viene poblado con el error de Vane y la UI no puede distinguir exito-con-fallback de fallo.
5. **`/health` no representa degradacion.** `web_search.search_endpoint` en realidad es el health de SearXNG (nombre confuso) y no hay `status: ok|degraded|error` ni `last_error`.
6. **Sin fallback de embedding configurable.** Si `qwen3-embedding:0.6b` no esta en Vane, deberia probar `bge-m3`.

## Plan de arreglo (implementado en esta sesion)

- `perplexica_client.py`: deteccion robusta de provider (name/id/baseUrl/forma de modelos), cache de providers con TTL, timeout separado para providers vs search, fallback de embedding, `last_error` observable, logging de provider/modelos/tiempos, metodos `detect_ollama_provider`, `detect_model`, `build_search_payload`, `normalize_response`.
- `web_search_service.py`: respuesta con `engine`, `fallback_used`, `vane_error`; `error=None` si el fallback funciono; `engine="none"` + `error="No web engine available"` si todo falla; sintesis con Ollama protegida por try/except.
- `health.py` + `schemas.py`: `searxng` top-level, `web_search.status` = ok/degraded/error, `fallback_available`, `last_error`.
- `settings.yaml`: `vane_search_timeout: 60`, `vane_fallback_embed_model: "bge-m3"`, `web_search_fallback: "searxng"`.
- `scripts/debug_vane_search.py`: prueba manual de providers + search con timeout 120s.
- Tests unitarios extendidos.

## Checks en vivo (correr en tu maquina)

```powershell
docker ps
docker ps -a
docker logs vane --tail 100
Invoke-RestMethod http://localhost:3000/api/providers
docker exec vane sh -c "wget -qO- http://host.docker.internal:11434/api/tags"
Invoke-RestMethod http://localhost:11434/api/tags
cd "C:\Users\angel\Modelo local\modelo-ia-carrera\backend"
.\.venv\Scripts\Activate.ps1
python .\scripts\debug_vane_search.py
```

Si `docker exec vane ... api/tags` falla: revisar que Ollama escuche en `0.0.0.0` (variable `OLLAMA_HOST=0.0.0.0`) y el firewall de Windows para el puerto 11434.
