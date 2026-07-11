# FINAL_AGENT_REPORT

Estado: 🟢 MVP seguro y funcional. 14 tests de seguridad. Verificado en vivo.

## Flujo
1. `POST /agent/sessions` — abre workspace (confinado a agent_workspace_base) e indexa árbol.
2. `POST /agent/sessions/{id}/plan` — LLM coder genera plan JSON (pasos edit/command validados).
3. `POST .../steps/{i}/propose` — genera diff unificado (NO escribe).
4. `POST .../steps/{i}/apply {approved:true}` — única vía de escritura/ejecución.
5. `reject` / `revert` — control total del usuario.

## Seguridad (SafetyPolicy — límites duros)
- Workspace dentro de `agent_workspace_base` (C:\Users\angel); fuera → 403.
- Rutas resueltas contra traversal (`..`), dirs excluidos (.git, node_modules, .ai-local…).
- **Secretos bloqueados** (lectura y escritura): .env, *.pem/*.key, id_rsa, credentials, *secret*.
- Escritura solo en extensiones de texto conocidas.
- Comandos: whitelist por prefijo (git status/diff/log, pytest, py_compile, npm lint/build/test,
  pip list), sin metacaracteres de shell, ejecutados con `shell=False` + `shutil.which`.
- **Nunca full-auto**: apply exige `approved=true` explícito; sin él → 403 y archivo intacto.

## Memoria y auditoría (por workspace, en .ai-local/)
- `actions.log` (JSONL): una línea por plan/apply/reject/revert con timestamp y detalles.
- `backups/`: copia física del archivo ANTES de cada apply (permite recuperación manual).
- `agent_state.json`: snapshot de la sesión tras cada acción (sobrevive reinicios del backend).

## Frontend (/agent)
Abrir workspace → objetivo → plan → diff coloreado (verde/rojo) → Aprobar/Rechazar/Revertir →
output de comandos → log de actividad. Placeholder anterior reemplazado.

## Verificado en vivo (2026-07-10)
- Sesión sobre agent-demo: plan real (qwen2.5-coder), diff correcto.
- apply sin aprobar → 403, archivo intacto; apply aprobado → cambio + backup + actions.log.
- C:\Windows → 403.

## Pendiente (fase agente PRO, en NEXT_AUTOPILOT_TASKS)
- Bucle iterativo (output de comando realimenta al LLM para el siguiente paso).
- Plan que lea contenido de archivos clave (hoy solo ve el árbol).
- Whitelist ampliada aprobable (pip/npm install, venv, git clone de github.com).
- Endpoints /agent/git/status|diff, /agent/index, /agent/search-files.
- Reload de sesiones desde agent_state.json al arrancar el backend.
