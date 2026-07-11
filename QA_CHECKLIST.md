# QA_CHECKLIST — verificación manual antes de dar por buena una sesión

## Automático (corre siempre)
- [ ] `cd backend ; .\scripts\test_all.ps1` → 57 passed, 1 skipped
- [ ] `cd frontend ; npm run lint` → sin errores
- [ ] `cd frontend ; npm run build` → Compiled successfully
- [ ] `npx playwright test` → 20 passed (18 screenshots + 2 menús)
- [ ] `cd backend ; .\scripts\check_gpu.ps1` → OK usando GPU

## Backend en vivo (requiere run_all)
- [ ] `/health` → status coherente (ok/degraded/error), no siempre "ok"
- [ ] `/chat` (mode general) → responde
- [ ] `/chat/stream` → emite meta→delta→done (NDJSON)
- [ ] `/rag/query` colección real → cita fuentes; pregunta trampa → "no relevante"
- [ ] `python scripts\eval_rag.py` → 15/15 reales, 5/5 trampas
- [ ] `/web/search` → engine vane o fallback searxng con fuentes
- [ ] `/documents/generate` (md y pdf) → archivo en outputs/ + descarga 200
- [ ] `/agent` crear sesión dentro de workspace_base → 200; fuera → 403

## Seguridad del agente
- [ ] Workspace fuera de base → 403
- [ ] Leer `.env` / `*.pem` → 403 (bloqueado)
- [ ] Comando fuera de whitelist → rechazado
- [ ] Comando con metacaracteres (`&&`, `|`, `;`) → rechazado
- [ ] apply sin `approved:true` → 403, archivo intacto
- [ ] apply aprobado → backup en `.ai-local/backups/` + línea en `actions.log`

## UI
- [ ] Toggle simple/pro → sidebar 9 ítems (pro) / 3 (simple)
- [ ] Modo simple redirige rutas pro a /chat
- [ ] Chat: streaming visible token a token
- [ ] Menús `+` y skill del composer abren sin crash
- [ ] `/documents`: generar → preview → descargar
- [ ] Historial de chat sobrevive F5
- [ ] Responsive: mobile arranca en simple

## Estado
- [ ] PROJECT_STATE.md actualizado
- [ ] NEXT_AUTOPILOT_TASKS.md refleja lo pendiente
- [ ] CHANGELOG_LOCAL.md con los cambios de la sesión
