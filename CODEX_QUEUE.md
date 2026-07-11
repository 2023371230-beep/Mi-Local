# CODEX_QUEUE — cola de tareas para Codex

Mantenida por el autopilot. Orden = prioridad. La sesion con acceso a Codex toma la primera
pendiente, actualiza estado aqui y en CODEX_WAIT_STATE.json.

| Task | Titulo | Estado | Spec |
|---|---|---|---|
| TASK-0004 | URGENTE: frontend gitlink -> carpeta del monorepo + push | pending | CODEX_TASKS/TASK-0004.md |
| TASK-0001 | Ingesta por lotes de PDFs pesados con split por capitulos | pending | CODEX_TASKS/TASK-0001.md |
| TASK-0002 | Agente PRO fase B: bucle iterativo con lectura de archivos | pending | CODEX_TASKS/TASK-0002.md |
| TASK-0003 | Router fino (F6) + RAG contextual en skills tematicas | pending | CODEX_TASKS/TASK-0003.md |

## Pendiente de la sesion Cowork (no requiere Codex)
- [x] `git push -u origin main` — RESUELTO 2026-07-11 por el usuario (188 objetos en origin/main).
      Remote origin ya configurado a https://github.com/2023371230-beep/Mi-Local.git.
      Ejecutar desde PowerShell del usuario o sesion Code con credenciales.
- [ ] Commitear los archivos de gobierno nuevos (CODEX_*/TASK-*) — git quedo inoperable en el
      sandbox Cowork por corrupcion de vista FUSE sobre .git/config (el archivo en disco esta
      integro; desde Windows funciona).
