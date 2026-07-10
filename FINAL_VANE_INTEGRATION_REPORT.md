# Final Vane Integration Report

Fecha: 2026-07-08

## Resumen

Se integro Vane, antes Perplexica, dentro de la carpeta `perplexica` del proyecto. Vane corre en Docker con la imagen `itzcrazykns1337/vane:latest`, expone su UI/API en `http://localhost:3000` y expone su SearXNG interno en `http://localhost:4000` para fallback controlado.

## Comandos ejecutados

```powershell
.\scripts\test_all.ps1
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/models
docker --version
docker ps
netstat -ano | findstr ":8000"
netstat -ano | findstr ":3000"
netstat -ano | findstr ":11434"
docker pull itzcrazykns1337/vane:latest
docker run -d -p 3000:3000 -p 4000:8080 -v vane-data:/home/vane/data --name vane itzcrazykns1337/vane:latest
Invoke-RestMethod http://localhost:3000/api/providers
Invoke-RestMethod "http://localhost:4000/search?q=OWASP%20Top%2010&format=json"
```

## Archivos creados o modificados

- `perplexica/README.md`
- `perplexica/scripts/run_vane.ps1`
- `perplexica/scripts/stop_vane.ps1`
- `perplexica/scripts/check_vane.ps1`
- `perplexica/scripts/logs_vane.ps1`
- `backend/scripts/check_vane_api.py`
- `backend/scripts/check_ports.ps1`
- `backend/scripts/stop_backend.ps1`
- `backend/scripts/fix_port_8000.ps1`
- `backend/scripts/run_all.ps1`
- `backend/scripts/stop_all.ps1`
- `backend/scripts/check_all.ps1`
- `backend/scripts/test_all.ps1`
- `backend/app/infrastructure/web/perplexica_client.py`
- `backend/app/infrastructure/web/searxng_client.py`
- `backend/app/application/services/web_search_service.py`
- `backend/app/presentation/endpoints/web_search.py`
- `backend/app/presentation/endpoints/health.py`
- `backend/app/domain/schemas.py`
- `backend/config/settings.yaml`
- `backend/config/.env.example`
- `backend/tests/test_vane_client.py`
- `backend/tests/test_web_search_integration.py`
- `backend/tests/test_web_search.py`
- `backend/README.md`
- `README.md`

## Docker

Resultado:

```text
vane Up
0.0.0.0:3000->3000/tcp
0.0.0.0:4000->8080/tcp
```

## Providers

`GET http://localhost:3000/api/providers` funciona.

Provider Ollama detectado:

```text
name: http://host.docker.internal:11434
chat model: qwen2.5:7b
embedding model: qwen3-embedding:0.6b
```

## Search API de Vane

`POST http://localhost:3000/api/search` fue probado con:

- `qwen2.5:7b` + `qwen3-embedding:0.6b`
- `llama3.2:latest` + `qwen3-embedding:0.6b`
- `llama3.2:latest` + `Xenova/all-MiniLM-L6-v2`

Resultado real: la API abre conexion pero no devuelve respuesta final dentro de 180-240 segundos. En modo stream devuelve `{"type":"init","data":"Stream connected"}` y luego queda esperando.

Diagnostico:

- Vane esta arriba.
- Ollama es visible desde Vane.
- `/api/providers` funciona.
- SearXNG interno funciona y devuelve resultados.
- Los logs de Vane/SearXNG muestran errores de motores externos 403/404 y timeouts.

Decision implementada:

El backend intenta Vane primero. Si `/api/search` falla o entra en timeout, usa SearXNG expuesto en `http://localhost:4000` y sintetiza la respuesta con Ollama local.

## Backend

`GET /health` con Vane prendido:

```json
{
  "status": "ok",
  "ollama": true,
  "chroma": true,
  "perplexica": true,
  "vane": true,
  "web_search": {
    "engine": "vane",
    "url": "http://localhost:3000",
    "providers_endpoint": true,
    "search_endpoint": true,
    "fallback_engine": "searxng",
    "fallback_url": "http://localhost:4000"
  }
}
```

`POST /web/search` funciona y devuelve respuesta con fuentes usando fallback SearXNG cuando Vane Search API hace timeout.

`POST /chat` con `mode=web` funciona y devuelve respuesta con fuentes.

## Pruebas

Resultado normal:

```text
23 passed, 1 skipped
```

Resultado integracion providers:

```text
1 passed
```

## Prueba con Vane apagado

Se detuvo el contenedor `vane`.

Resultado:

- `/health` siguio respondiendo `status: ok`.
- `vane: false`.
- `/web/search` devolvio error controlado sin tumbar el backend.

## Pendientes

- Investigar por que `POST /api/search` de Vane queda en timeout aunque SearXNG interno si devuelve resultados.
- Revisar futuras versiones de la imagen `itzcrazykns1337/vane:latest`.
- Considerar configurar motores SearXNG para reducir 403/404 externos.
- Mantener fallback SearXNG como camino estable de produccion local.

## Recomendacion final

Para este hardware y entorno local, mantener Vane para UI/providers y usar SearXNG como fallback operativo del backend es la opcion mas estable. El backend ya no depende de que Vane Search API termine correctamente y conserva fuentes web reales.
