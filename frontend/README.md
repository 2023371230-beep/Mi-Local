# Modelo IA Carrera Frontend

Frontend tipo centro de comando para el asistente local de IA, RAG, skills, modelos, logs y modo agente preparado.

## Requisitos

- Node.js
- Backend activo en `http://127.0.0.1:8000`

## Variables

```env
NEXT_PUBLIC_BACKEND_URL=http://127.0.0.1:8000
```

## Comandos

```powershell
cd "C:\Users\angel\Modelo local\modelo-ia-carrera\frontend"
npm install
npm run dev -- -p 3001
npm run lint
npm run build
```

Nota: `3000` esta usado por Vane. Usa `3001` para el frontend local.

## Rutas

- `/`
- `/chat`
- `/skills`
- `/rag`
- `/documents`
- `/models`
- `/logs`
- `/agent`
- `/settings`

## Pruebas visuales (Playwright)

```powershell
cd "C:\Users\angel\Modelo local\modelo-ia-carrera\frontend"
npm run dev -- -p 3001      # terminal 1: servidor
npm run test:ui             # terminal 2: pruebas + screenshots
```

Las capturas quedan en `test-results/ui-screenshots/` (una por ruta, desktop y mobile). Para regenerarlas con estados reales, enciende el backend antes de correr `test:ui`.

## Interpretar el estado web / Vane

- `web: ok` — Vane responde busquedas normalmente.
- `web: fallback` — Vane fallo o dio timeout; el backend uso SearXNG. La respuesta sigue siendo valida.
- `vane: degraded` — Vane responde `/api/providers` pero no completa `/api/search`.
- En `/logs`, los timeouts de Vane se agrupan ("Vane search timed out × N") con card de diagnostico.
- Recomendacion mientras Vane este lento: mantener el fallback SearXNG activo (ver `/settings` → Web search).

## Como usar la UI refinada

- Dashboard (`/`): estado general, acciones rapidas y actividad reciente.
- Chat (`/chat`): opciones avanzadas (modo, RAG, coleccion, top_k) viven en el accordion del input; fuentes en el panel derecho.
- Skills (`/skills`): boton "Probar" selecciona la skill en el playground unico de abajo.
- RAG/Documents: flujo guiado; la ingesta no modifica tus PDFs originales.
- Logs (`/logs`): filtra por severidad (INFO/WARNING/ERROR) o dominio (Vane, chat, RAG, web).
- Settings (`/settings`): agrupado en Backend / Chat / Apariencia / Web search / Avanzado; persiste en localStorage.

## Troubleshooting

- Backend apagado: `cd backend; .\scripts\run_all.ps1`
- Puerto `3000` ocupado: usar `npm run dev -- -p 3001`
- CORS: backend ya permite `localhost/127.0.0.1` en `3000` y `3001`
- Ollama apagado: revisar `http://localhost:11434/api/tags`
- Vane apagado: `cd perplexica; .\scripts\run_vane.ps1`
- Vane lento en busqueda: backend cae a SearXNG; ajustar `vane_search_timeout` en `backend/config/settings.yaml`
- RAG sin documentos: usar `/documents` o `POST /ingest`
- Error de build: ejecutar `npm run lint` y revisar tipos

## Estado

`npm run lint` y `npm run build` pasan.
