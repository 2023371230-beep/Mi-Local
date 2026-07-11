# PLAYWRIGHT_SCREENSHOTS_REPORT

Suite: `tests/ui-smoke.spec.ts`. 20 tests, todos en verde (2026-07-10).

## Cobertura
- **18 screenshots**: 9 rutas × 2 viewports (desktop 1440×1000, mobile Pixel 7).
  Rutas: dashboard, chat, skills, rag, documents, models, logs, agent, settings.
  Cada uno verifica: sin "Unhandled Runtime Error"/"Build Error"/"Application error",
  sin errores de consola (excepto favicon), y guarda PNG en test-results/ui-screenshots/.
- **2 interactivos** ("Chat composer menus"): abre el menú `+` y el selector de skill,
  verifica que renderizan sin crash ni errores de consola (regresión del bug de DropdownMenuLabel).

## Requisito
El backend debe estar corriendo (:8000) o algunas páginas registran ERR_CONNECTION_REFUSED en
consola y los tests fallan. La suite levanta su propio dev server en :3001.

## Correr
```powershell
cd frontend
npx playwright test                 # todo
npx playwright test --grep composer # solo los interactivos
```

Screenshots regenerados en cada corrida; sirven de regresión visual básica.
