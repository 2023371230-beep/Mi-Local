# UI Refinement Status

Fecha: 2026-07-08

## Validacion base

Frontend:

```text
npm run lint: ok
npm run build: ok
```

Backend:

```text
.\scripts\test_all.ps1: 23 passed, 1 skipped
GET /health: ok
GET /models: ok, 5 modelos
GET /rag/collections: ok, ui_ux
```

## Health observado

```text
api: ok
ollama: ok
chroma: ok
vane/perplexica: off
searxng fallback endpoint: off
```

Nota: el backend responde correctamente, pero los servicios web externos actuales aparecen no disponibles desde `/health`. La UI debe mostrar esto como estado degradado/off, no como exito total.

## Rutas existentes

- `/`
- `/chat`
- `/skills`
- `/rag`
- `/documents`
- `/models`
- `/logs`
- `/agent`
- `/settings`

## Riesgos detectados

- El cliente API usa `NEXT_PUBLIC_BACKEND_URL`; no conviene cambiar contrato en esta fase.
- El panel derecho depende de `useChatStore.sources`; debe conservarse.
- Chat y RAG actualizan fuentes globales; no romper ese flujo.
- `Button` local no soporta `asChild`; evitar ese patron.
- Vane/SearXNG pueden estar off o degradados; la UI debe tolerar campos incompletos.
- Settings persiste con Zustand; no borrar keys existentes.

## Que NO se tocara

- No se implementara modo agente real.
- No se cambiaran endpoints.
- No se cambiara arquitectura backend.
- No se borraran rutas.
- No se borraran stores.
- No se eliminara ninguna funcionalidad actual.

## Plan corto de cambios

1. Agregar QA visual con Playwright y screenshots.
2. Crear design system interno con surfaces, status badges y cards reutilizables.
3. Redefinir layout: sidebar jerarquica, topbar con estados reales y panel derecho inteligente.
4. Refinar rutas principales con progressive disclosure.
5. Ejecutar lint, build, pruebas UI y generar reporte final.

## Estado

```text
Fase 0: completada
```
