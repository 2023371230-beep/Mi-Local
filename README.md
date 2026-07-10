# Modelo IA Carrera

Asistente local modular para Redes, Ciberseguridad, programacion, UI/UX, bases de datos, RAG local y busqueda web.

La implementacion se trabaja por fases con validacion antes de avanzar.

## Estado actual

- Backend FastAPI en `backend`.
- RAG local con ChromaDB persistente.
- Vane/Perplexica en Docker dentro de `perplexica`.
- Vane UI/API: `http://localhost:3000`.
- SearXNG interno de Vane expuesto en `http://localhost:4000`.
- Backend: `http://127.0.0.1:8000`.
- Web search usa Vane primero y SearXNG como fallback; `vane_search_timeout` esta en `backend/config/settings.yaml`.

## Arranque rapido

```powershell
cd "C:\Users\angel\Modelo local\modelo-ia-carrera\backend"
.\scripts\run_all.ps1
```

Frontend:

```powershell
cd "C:\Users\angel\Modelo local\modelo-ia-carrera\frontend"
npm install
npm run dev -- -p 3001
```

Abrir:

```text
http://127.0.0.1:3001
```

## Pruebas

```powershell
cd "C:\Users\angel\Modelo local\modelo-ia-carrera\backend"
.\scripts\test_all.ps1
.\scripts\test_all.ps1 -Integration
```

Frontend:

```powershell
cd "C:\Users\angel\Modelo local\modelo-ia-carrera\frontend"
npm run lint
npm run build
```
