# NEXT_AUTOPILOT_TASKS — cola de trabajo del autopilot

Orden por impacto. Al retomar una sesión: leer PROJECT_STATE.md + este archivo y continuar.

## En curso
- [ ] **Agente PRO fase B**: bucle iterativo (output de comando → LLM propone siguiente paso,
      siempre con aprobación); plan lee contenido de archivos clave, no solo el árbol.
- [ ] **Agente PRO fase C**: whitelist ampliada aprobable (pip/npm install, python -m venv,
      git clone de github.com) — cada ejecución sigue requiriendo aprobación.
- [ ] **F6 Router fino**: podar patrones sobre-anchos (\berror\b, \bapi\b, \blogs?\b), 2ª
      pasada con llama3.2 cuando ninguna regex matchee, ui_ux → modelo general.
- [ ] **RAG contextual en skills temáticas**: mini-query a la colección de la skill y añadir
      contexto si distancia ≤ umbral.
- [ ] **Ingestar PDFs grandes por lotes** (con dedup ya barato). NO ingestar refman completo.
- [ ] **README raíz + backend + frontend** actualizados (fase 12) + ARCHITECTURE.md.
- [ ] **QA_CHECKLIST.md** + reportes finales por área (fase 13).
- [ ] Puertos del contenedor vane publicados en 0.0.0.0 → republicar como 127.0.0.1 (requiere
      recrear contenedor; coordinar con usuario).

## Requiere permiso del usuario
- [ ] Commits de F1/F2+ (el baseline está commiteado; el resto del trabajo está uncommitted).
- [ ] Ingesta masiva de PDFs pesados (horas de GPU/CPU).
- [ ] Recrear contenedor vane con puertos en 127.0.0.1.
