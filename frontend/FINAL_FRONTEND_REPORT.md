# Final Frontend Report

Fecha: 2026-07-08

## Que se creo

Frontend Next.js App Router con TypeScript, Tailwind CSS, shadcn/ui, TanStack Query, Zustand, Zod, React Markdown y syntax highlighting.

La UI usa el brief generado desde RAG:

```text
C:\Users\angel\Modelo local\modelo-ia-carrera\frontend-design-brief.md
```

## Rutas

- `/` Dashboard
- `/chat` Chat principal
- `/skills` Skills
- `/rag` Consulta RAG
- `/documents` Ingesta de documentos
- `/models` Modelos y sistema
- `/logs` Logs
- `/agent` Modo agente preparado
- `/settings` Preferencias locales

## Endpoints consumidos

- `GET /health`
- `GET /models`
- `POST /chat`
- `POST /ingest`
- `GET /rag/collections`
- `POST /rag/query`
- `POST /web/search`
- `GET /logs`

## Pruebas pasadas

Backend:

```text
23 passed, 1 skipped
```

Frontend:

```text
npm run lint
npm run build
```

Rutas UI verificadas en dev server:

```text
/ 200
/chat 200
/skills 200
/rag 200
/documents 200
/models 200
/logs 200
/agent 200
/settings 200
```

Flujos backend usados por la UI:

```text
general 200 skill=skill_chat_general
programacion 200 skill=skill_programacion
ui_ux 200 skill=skill_ui_ux
ciberseguridad 200 skill=skill_ciberseguridad
bases_datos 200 skill=skill_bases_datos
rag 200 skill=skill_rag_local sources=2
web 200 engine=searxng sources=1 error="Vane search timed out after 8.0 seconds."
```

## Errores encontrados

- shadcn inicializo en `src/`; se movio a estructura raiz como pedia el loop.
- `TooltipProvider` no acepta `delayDuration` en esta version; se retiro.
- `Button` no soporta `asChild` en esta version; se reemplazo por `Link` estilizado.
- ESLint marco un hook generado por shadcn; se ajusto `use-mobile.ts`.
- Backend requeria CORS para browser; se agrego CORS limitado a `localhost/127.0.0.1` en puertos `3000` y `3001`.
- Puerto `3000` esta ocupado por Vane; frontend dev se valido en `3001`.
- Vane responde `/api/providers`, pero `/api/search` sigue tardando demasiado; se dejo fallback a SearXNG y timeout configurable `vane_search_timeout: 8.0`.

## Como correr frontend

```powershell
cd "C:\Users\angel\Modelo local\modelo-ia-carrera\frontend"
npm install
npm run dev -- -p 3001
npm run build
```

## Como correr backend

```powershell
cd "C:\Users\angel\Modelo local\modelo-ia-carrera\backend"
.\scripts\run_all.ps1
```

## Modo agente real pendiente

La pantalla `/agent` deja preparada la estructura visual de file explorer, diff preview, aprobaciones y terminal. Falta crear endpoints backend para:

- abrir carpetas locales
- listar archivos
- leer archivos
- proponer diffs
- aprobar cambios
- ejecutar comandos con permiso
- registrar auditoria de acciones

## Proximos pasos

- Diagnosticar por que Vane `/api/search` no completa antes del timeout aunque `/api/providers` responde.
- Agregar endpoints reales para modo agente.
- Agregar streaming de chat si el backend lo soporta.
- Mejorar virtualizacion de logs si crecen mucho.
- Agregar tests Playwright para flujos de UI.
- Permitir configurar `NEXT_PUBLIC_BACKEND_URL` desde settings runtime.
