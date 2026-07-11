# NEXT_AUTOPILOT_TASKS — cola de trabajo del autopilot

Orden por impacto. Al retomar una sesión: leer PROJECT_STATE.md + este archivo y continuar.

## En curso
- [ ] **Agente PRO fase B** → especificado en CODEX_TASKS/TASK-0002.md (pendiente Codex).
- [ ] **Agente PRO fase C**: whitelist ampliada aprobable (pip/npm install, python -m venv,
      git clone de github.com) — cada ejecución sigue requiriendo aprobación.
- [ ] **F6 Router fino + RAG contextual** → especificado en CODEX_TASKS/TASK-0003.md (pendiente Codex).
- [ ] **RAG contextual en skills temáticas**: mini-query a la colección de la skill y añadir
      contexto si distancia ≤ umbral.
- [ ] **Ingestar PDFs grandes por lotes** → especificado en CODEX_TASKS/TASK-0001.md (pendiente Codex).
- [ ] **README raíz + backend + frontend** actualizados (fase 12) + ARCHITECTURE.md.
- [ ] **QA_CHECKLIST.md** + reportes finales por área (fase 13).
- [ ] Puertos del contenedor vane publicados en 0.0.0.0 → republicar como 127.0.0.1 (requiere
      recrear contenedor; coordinar con usuario).

## Requiere permiso del usuario
- [x] Commits de F1/F2+ — HECHO 2026-07-11 (autopilot Cowork, autorizado por prompt maestro).
- [ ] `git push -u origin main` — requiere credenciales del usuario (remote ya configurado).
- [ ] Ingesta masiva de PDFs pesados (horas de GPU/CPU).
- [ ] Recrear contenedor vane con puertos en 127.0.0.1.
