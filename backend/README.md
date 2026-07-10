# Backend - Modelo IA Carrera

Backend local para un asistente de IA con FastAPI, Ollama, ChromaDB, RAG condicional, skills y busqueda web controlada.

## Estado

- Fase 0: auditoria de entorno validada.
- Fase 1: estructura base y `/health`.
- Fase 2: cliente Ollama y `/models`.
- Fase 3: ChromaDB persistente.
- Fase 4: ingesta PDF, chunking, deduplicacion y `/rag/query`.
- Fase 5: router condicional y skills iniciales.
- Fase 6: `/chat` uniforme.
- Fase 7 parcial: `/web/search` con adaptador Vane/Perplexica preparado y fallback controlado.
- Fase 8: logs basicos y `/logs`.
- Fase Vane: Docker con Vane en `3000`, SearXNG interno expuesto en `4000`, provider Ollama detectado y fallback web funcional.

## Ejecutar

```powershell
cd "C:\Users\angel\Modelo local\modelo-ia-carrera\backend"
.\scripts\setup_env.ps1
.\scripts\run_all.ps1
```

O solo backend:

```powershell
.\scripts\run_backend.ps1
```

## Probar

```powershell
.\scripts\test_all.ps1
Invoke-RestMethod http://127.0.0.1:8000/health
```

## Endpoints principales

- `GET /health`
- `GET /models`
- `POST /chat`
- `POST /ingest`
- `GET /rag/collections`
- `POST /rag/query`
- `POST /web/search`
- `GET /logs`

## Ejemplo de ingesta controlada

```powershell
$body = @{
  path = "C:\Users\angel\Modelo local\RAG\UI\User_Research_Methods_A4-compressed (1).pdf"
  collection = "ui_ux"
  topic = "ui_ux"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/ingest" -Method Post -ContentType "application/json" -Body $body
```

## Nota sobre Perplexica/Vane

El upstream actual usa el nombre Vane, antes Perplexica. El backend mantiene la carpeta `perplexica`.

Vane corre en:

- UI/API: `http://localhost:3000`
- Providers: `http://localhost:3000/api/providers`
- Search API: `http://localhost:3000/api/search`
- SearXNG interno expuesto como fallback: `http://localhost:4000`

Si Vane corre en Docker y Ollama corre en Windows, la URL de Ollama dentro de Vane debe ser:

```text
http://host.docker.internal:11434
```

En este entorno, `/api/providers` funciona y detecta Ollama con `qwen2.5:7b` y `qwen3-embedding:0.6b`. La llamada directa a `/api/search` queda en timeout; por eso el backend intenta Vane primero y usa SearXNG como fallback controlado, devolviendo fuentes al usuario sin tumbar el backend.

## Fix Vane (2026-07-08)

El cliente Vane fue endurecido; ver `reports/VANE_AUDIT.md` y `reports/FINAL_VANE_FIX_REPORT.md`.

- `vane_search_timeout: 60` (una busqueda Perplexica con LLM local tarda 30-120s; con 8s el timeout era garantizado).
- Deteccion robusta del provider Ollama (name/id/baseUrl/forma de modelos) + cache de providers.
- Fallback de embedding a `bge-m3` si falta `qwen3-embedding`.
- `/web/search` ahora devuelve `engine` (vane|searxng|none), `fallback_used` y `vane_error`; `error=null` si el fallback respondio.
- `/health` incluye `searxng` y `web_search.status` (ok|degraded|error) con `last_error`.
- La ingesta acepta ahora `.pdf`, `.md` y `.txt` (guias curadas nuevas en `C:\Users\angel\Modelo local\RAG`).

Debug end-to-end de Vane:

```powershell
.\.venv\Scripts\Activate.ps1
python .\scripts\debug_vane_search.py "What is OWASP?"
```

## Scripts operativos

```powershell
.\scripts\check_ports.ps1
.\scripts\run_all.ps1
.\scripts\stop_all.ps1
.\scripts\test_all.ps1
.\scripts\test_all.ps1 -Integration
.\scripts\check_all.ps1
```

Vane:

```powershell
cd "C:\Users\angel\Modelo local\modelo-ia-carrera\perplexica"
.\scripts\run_vane.ps1
.\scripts\check_vane.ps1
.\scripts\logs_vane.ps1
.\scripts\stop_vane.ps1
```

## Troubleshooting Vane

- Puerto `8000` ocupado: `.\scripts\check_ports.ps1`, luego `.\scripts\run_backend.ps1 -Port 8010` o `.\scripts\fix_port_8000.ps1 -Kill`.
- Puerto `3000` ocupado: `.\scripts\run_vane.ps1 -Port 3001`, y cambia `PERPLEXICA_URL`.
- Docker apagado: abre Docker Desktop o ejecuta `.\scripts\run_all.ps1` después de iniciarlo.
- Ollama no visible desde contenedor: prueba `docker exec vane sh -c "curl -s http://host.docker.internal:11434/api/tags"`.
- Vane responde sin sources o con timeout: revisar `docker logs vane --tail 100`; el backend usara SearXNG en `4000`.
- SearXNG bloqueado por motores externos: Vane puede mostrar errores 403/404 de algunos motores, pero DuckDuckGo suele devolver resultados.
