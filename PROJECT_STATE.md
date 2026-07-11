# PROJECT_STATE — Modelo IA Carrera

Actualizado: 2026-07-10 (sesión autopilot Code). Fuente de verdad del estado real.

## Qué es
Plataforma local de IA: FastAPI (:8000) + Ollama + ChromaDB + Vane/SearXNG (docker :3000/:4000)
+ Next.js 16 (:3001). Solo modelos locales, sin APIs de pago. Regla de oro del agente: nada se
escribe/ejecuta sin aprobación explícita del usuario.

## Estado por componente

| Componente | Estado | Detalle |
|---|---|---|
| Backend FastAPI | 🟢 estable | 60 tests, health real, /chat/stream, /documents/*, /agent/* |
| Ollama | 🟢 con watchdog | RTX 3060 detectada; `scripts/check_gpu.ps1 -Fix` si cae a CPU tras suspender |
| RAG | 🟢 calibrado | eval_rag.py 20/20; umbral rag_max_distance=1.03 (L2², bge-m3) |
| Web search | 🟢 confiable | Vane streaming + abort temprano sin fuentes + fallback SearXNG (~1:15 total) |
| Modo agente | 🟢 MVP seguro | plan→diff→apply aprobado; secretos bloqueados; backups+actions.log+persist en .ai-local |
| Frontend | 🟢 | lint+build+20 Playwright; modo simple/pro + Motion; generador de documentos |
| Git | 🟢 | Repo iniciado 2026-07-10, baseline + trabajo F1/F2 sin commitear (pedir permiso) |

## Config crítica (no perder)
- Env usuario: `OLLAMA_MAX_LOADED_MODELS=2`, `OLLAMA_NUM_PARALLEL=1`
- settings.yaml: vane con llama3.2+bge-m3; RAG embed bge-m3; ollama_timeout 300;
  vane_search_timeout 180; rag_max_distance 1.03; agent_workspace_base C:\Users\angel
- Vane SOLO funciona por streaming (stream:false cuelga para siempre — bug del fork)
- Colecciones Chroma (bge-m3): asistente, programacion, bases_datos, ciberseguridad, ui_ux

## Cómo arrancar todo
```powershell
cd "C:\Users\angel\Modelo local\modelo-ia-carrera\backend"
.\scripts\run_all.ps1     # docker+vane+watchdog GPU+backend
cd ..\frontend ; npm run dev -- -p 3001
```

## Fases de la auditoría (PROJECT_AUDIT_REPORT.md)
- F1 quick wins: ✅ COMPLETA (2026-07-10)
- F2 calidad RAG: ✅ COMPLETA (2026-07-10)
- F3 streaming chat: ✅ COMPLETA (2026-07-10) — /chat/stream NDJSON + UI token a token
- Skill documentos: ✅ COMPLETA (MD/HTML/DOCX/PDF con RAG opcional)
- UI simple/pro + Motion: ✅ COMPLETA
- F4-F5 agente PRO: pendiente
- F6 router fino: parcial (patrones cyber afinados, regla de aclaración en skills; falta router LLM 2ª pasada)
- Memoria .ai-local (backups/actions.log/state): ✅ COMPLETA
- Documentación completa (README, ARCHITECTURE, reportes finales, QA_CHECKLIST): ✅ COMPLETA

## Ciclo autopilot Cowork 2026-07-11

- Git: 3 commits nuevos en main (estado autopilot, backend F1-F3+agente+documentos, gobierno).
  Repo frontend anidado: 1 commit (streaming+composer+Motion+docs-generator).
- Remote `origin` configurado: https://github.com/2023371230-beep/Mi-Local.git
- **PUSH PENDIENTE** (bloqueo real: credenciales GitHub). Ejecutar desde PowerShell:
  `cd "C:\Users\angel\Modelo local\modelo-ia-carrera"; git push -u origin main`
- Codex: NO disponible en sandbox Cowork (npm 403). Cola y specs creadas:
  CODEX_QUEUE.md, CODEX_WAIT_STATE.json, CODEX_TASKS/TASK-0001..0003.
- Incidente: `git remote add` corrompio la vista FUSE de .git/config en el sandbox
  (archivo en disco INTEGRO, reconstruido completo). Git funciona desde Windows;
  desde este sandbox quedo inoperable el resto de la sesion.
- Los archivos de gobierno nuevos (CODEX_*) quedan sin commitear: commitearlos desde
  la sesion Code junto con TASK-0001.

## Update 2026-07-11 (post-push)
- Push a origin/main COMPLETADO (usuario). Bloqueo credenciales RESUELTO.
- CRITICO detectado: frontend viajo como gitlink 160000 => GitHub main NO tiene el codigo
  frontend. Fix especificado en CODEX_TASKS/TASK-0004.md (prioridad 1 de la cola).
- .gitignore raiz parcheado: .env.* / *.env.local (antes .env.local NO estaba cubierto y
  se habria subido al des-anidar el frontend).
- No iniciar funciones grandes hasta cerrar TASK-0004 (regla del propietario).
