# PROJECT_AUDIT_REPORT — Modelo IA Carrera

Auditoría de solo lectura, 2026-07-10. Basada en lectura directa del código, mediciones en vivo
(latencias reales medidas hoy) y los logs de Ollama/Vane/backend. **Nada fue modificado** salvo
dos excepciones acordadas: el hotfix del crash del menú `+` en `/chat` (con test de regresión) y
un reinicio diagnóstico de Ollama.

---

## 1. Resumen ejecutivo

El proyecto está **sano y bien estructurado** (clean architecture real en backend, 46 tests en
verde, frontend consistente). Los tres hallazgos que cambian el juego:

1. **Tu RTX 3060 existe, funciona, y Ollama la ignora de forma intermitente.** Medido hoy:
   misma máquina, mismo modelo — 7 tok/s (CPU) vs **98 tok/s** (GPU) con llama3.2, y **27 tok/s**
   con qwen2.5:7b. Toda la lentitud crónica del proyecto (búsquedas de 4 min, timeouts de RAG)
   viene de arranques donde la detección CUDA falla (típicamente tras suspender la laptop) y
   Ollama cae a CPU **en silencio**. Es el fix de mayor impacto de todo el reporte.
2. **No hay repositorio git.** Con un agente que edita archivos y un bug conocido de truncado en
   Cowork, trabajar sin control de versiones es el mayor riesgo operativo del proyecto.
3. **El chat no hace streaming.** Con GPU a 27-98 tok/s, streaming convertiría la experiencia de
   "esperar 30-60s mirando un spinner" a "ver la respuesta fluir al instante".

## 2. Estado general

| Área | Estado | Nota |
|---|---|---|
| Backend arquitectura | 🟢 | Capas limpias, DI por Depends, schemas Pydantic completos |
| Tests backend | 🟢 82% cov | 46 pass; débiles en chat_service (43%) y rag_service (33%) |
| Frontend | 🟢 | lint/build/20 tests Playwright; crash del composer ya corregido |
| Ollama | 🔴 | GPU intermitente (hallazgo crítico #1) |
| RAG | 🟡 | Funciona; sin umbral de score, sin reranking, ingesta re-embebe duplicados |
| Vane/SearXNG | 🟡 | Estable vía streaming + fallback; pierde ~2 min cuando Vane no tiene fuentes |
| Modo agente | 🟡 | MVP sólido con aprobación; 4 huecos de seguridad listados abajo |
| Git / respaldos | 🔴 | Inexistentes |

## 3. Hallazgos críticos

### C1 — Ollama corre en CPU tras ciertos arranques (impacto: 4-14× en todo)
Evidencia: `%LOCALAPPDATA%\Ollama\server.log` de hoy 11:23 — descubrimiento solo encontró
`Vulkan0 (AMD Radeon)` y cayó a `inference compute id=cpu`. Reinicio a las 16:38: `CUDA0 NVIDIA
GeForce RTX 3060 Laptop GPU, compute=8.6, 6.0 GiB` y `nvidia-smi` sano (driver 592.00, CUDA 13.1).
Es intermitente — probablemente el runtime CUDA no responde justo tras resume/boot (Optimus).
**Fix propuesto**: watchdog en `backend/scripts/check_all.ps1` (o tarea programada al resume):
generar 1 token y leer `size_vram` de `/api/ps`; si es 0 → reiniciar `ollama app.exe`. Riesgo: nulo.

### C2 — Sin git
`modelo-ia-carrera/` no es repo. El modo agente escribe archivos, Cowork tiene bug de truncado
documentado, y no hay forma de auditar/revertir nada. **Fix**: `git init` + `.gitignore`
(node_modules, .venv, .next, data/chroma, logs, test-results) + commit inicial. Riesgo: nulo.
Además habilita la mejora A4 del agente (rollback por git en vez de backups en RAM).

### C3 — Crash del menú `+` del composer (YA CORREGIDO como hotfix)
`chat-input.tsx` usaba `DropdownMenuLabel` (= `Menu.GroupLabel` de Base UI) sin `DropdownMenuGroup`
padre → crash al abrir el menú. Corregido + test de regresión que abre ambos menús
(`tests/ui-smoke.spec.ts`, describe "Chat composer menus"). Lección incorporada: los smoke tests
solo hacían render; los menús no se montaban.

### C4 — `/health` siempre reporta `status: "ok"`
`endpoints/health.py:38`: `HealthResponse(status="ok", ...)` es literal — aunque Ollama y Chroma
estén caídos. El frontend (top-bar) muestra verde con el backend medio muerto. Fix de 3 líneas:
derivar status de los checks. Riesgo: bajo (el frontend ya lee los campos individuales).

## 4. Hallazgos medios

### M1 — Agente: 4 huecos de seguridad (mi propio módulo, auditoría honesta)
- **`npm`/comandos .cmd no ejecutan en Windows**: `subprocess.run(tokens, shell=False)` en
  `agent_service.py:_run_command` no resuelve `npm.cmd` → "Ejecutable no encontrado". Fix:
  `shutil.which(tokens[0])`.
- **Secretos legibles**: `SafetyPolicy.validate_read` no bloquea `.env`, `*.pem`, `id_rsa`…
  (el árbol los oculta por empezar con ".", pero `GET /agent/sessions/{id}/file?path=.env` los lee).
  Fix: deny-list de patrones de secretos en `resolve_inside`.
- **Sin auditoría persistente ni backups en disco**: eventos y `original_content` viven en RAM
  (`AgentSession`); un reinicio del backend pierde el historial y la capacidad de revert. Fix:
  JSONL por sesión en `backend/logs/agent/` + backup físico antes de cada apply.
- **Prompt injection desde archivos**: el contenido de un archivo malicioso entra al prompt del
  LLM en `propose_edit`. Mitigación existente: el humano aprueba cada diff/comando (por eso el
  diseño no-full-auto es correcto). Mitigación extra: instrucción anti-injection en
  `_EDIT_SYSTEM_PROMPT` y marcar el contenido como datos no confiables.

### M2 — Router por regex con patrones sobre-anchos (`routing_rules.py`)
- `\blogs?\b` y `ataque` mandan a ciberseguridad mensajes inocentes ("logs de mi app Next").
- `\berror\b` y `\bapi\b` capturan casi cualquier duda técnica hacia programación.
- Orden fijo cyber→db→ui→prog: "SQL injection en mi query" gana cyber (bien) pero
  "optimiza mi query" con la palabra "index" cae en db aunque sea de Chroma.
- `ollama_router_model: llama3.2` en settings **no se usa en ningún sitio** — el router es 100%
  regex (config muerta, confunde). Opciones: borrar la clave, o implementar router LLM de 2ª
  pasada solo cuando ninguna regex matchea (llama3.2 a 98 tok/s lo hace viable, ~1s).
- `skill_ui_ux` usa `ollama_coder_model` (query_router.py:59) — para prosa de diseño el general
  da mejores respuestas; coder solo si piden código de UI.

### M3 — RAG sin umbral de calidad ni reranking (`rag_service.py`)
- `answer()` mete los top_k al prompt **sin filtrar por distancia**: si preguntas algo que no está
  en los docs, el 7B recibe 5 chunks irrelevantes e igual "responde" (alucinación con citas).
  Fix: umbral de distancia (medir con el dataset de abajo; típico coseno <0.6-0.7 con bge-m3) y
  responder "no está en tus documentos" si nada pasa.
- Sin reranking: con bge-m3 ya cargado, un rerank barato es reordenar por distancia + boost si el
  término aparece literal en el chunk. (Cross-encoder real = otro modelo; no lo recomiendo en 16GB.)
- `SKILL_COLLECTIONS` default `"general"` no existe → `get_or_create_collection` la **crea vacía**
  como efecto secundario de una query (chroma_client.py:query usa get_or_create). Fix: usar `get_collection` en queries y 404 limpio.
- Síntesis siempre con qwen2.5:7b + `num_ctx 4096`: 5 chunks×1000 chars + prompt ≈ 1.5-2k tokens,
  cabe, pero con top_k 12 (opción del composer nuevo) se trunca silenciosamente. Fix: num_ctx 8192
  ahora que hay GPU.

### M4 — Ingesta re-embebe duplicados (`ingestion_service.py:_ingest_file`)
Embebe TODOS los chunks y después `add_documents` descarta los ya existentes → re-ingestar la
carpeta RAG entera paga el costo completo de embeddings aunque no cambie nada (verificado hoy:
`native_mobile_design_guide.pdf` re-ingestado = 22 duplicates_skipped pero pagó 22 embeddings).
Fix: consultar `collection.get(ids=...)` ANTES de embeber. Ahorro enorme para tu plan de ingestar
los PDFs grandes.

### M5 — Vane pierde ~2 min generando respuestas que se van a descartar
`web_search_service.search_and_answer` espera la respuesta completa de Vane y la descarta si no
trae fuentes. En el stream, `sources` llega ANTES del primer token de respuesta
(verificado en el código del fork: emite `searchResults` antes del LLM). Fix en
`perplexica_client._post_search`: si llega el primer `response` sin `sources` previos → abortar y
saltar directo al fallback. Ahorra 1-2 min en cada búsqueda sin resultados.

### M6 — Sin streaming de chat (endpoint y UI)
`POST /chat` es síncrono; el frontend espera todo con un spinner. Con GPU es LA mejora de UX:
`StreamingResponse` NDJSON en FastAPI + lector en `chat-view.tsx`. Afecta: `endpoints/chat.py`,
`ollama_client.py` (nuevo `chat_stream`), `base_skill.py`, `lib/api/chat.ts`, `chat-view.tsx`.
Riesgo: medio (toca el camino principal) — hacerlo como endpoint nuevo `/chat/stream` y migrar la
UI cuando esté probado.

### M7 — Frontend: detección de fallback rota y historial no persistente
- `chat-view.tsx:19`: infiere fallback con `source.source === "searxng"`, pero los sources del
  fallback traen el nombre del engine real ("google", "brave"…) — el toast casi nunca dispara.
  El backend YA manda `web_fallback_used`; úsalo.
- `chat-store.ts`: sin `persist` — F5 borra la conversación. Zustand persist a localStorage = 3 líneas.
- `sidebar-section.tsx` quedó huérfano tras la sidebar plana de Cowork (verificar y borrar).

## 5. Hallazgos bajos

- `keep_alive` no se envía en requests → modelos se descargan a los 5 min; con GPU la recarga es
  6-10s, tolerable, pero para el modelo de chat activo conviene `keep_alive: "30m"` en options.
- `ollama_client.py:17` health con timeout 5s fijo; `/health` construye un `ChromaVectorClient`
  nuevo (abre sqlite de chroma) en cada llamada — cachearlo como singleton en dependencies.
- `read_recent_logs` lee el archivo completo para devolver 100 líneas (logger.py:30) — fine hoy
  (rota a 5MB), mejorable con lectura por cola.
- `_EDITABLE_SUFFIXES` del agente no permite crear archivos sin extensión (Makefile, Dockerfile).
- PM² (docx/xlsx) no se ingesta — pypdf no los soporta y la ingesta los ignora en silencio;
  decidir: soporte docx (python-docx) o documentar que solo PDF/MD/TXT.
- `test_web_search_integration.py` skipped por default (bien) pero nadie lo corre — añadirlo al
  checklist manual.

## 6. Quick wins (aprobables en bloque, <1h total, riesgo mínimo)

1. Watchdog GPU en `check_all.ps1`/`run_all.ps1` (C1) — el de mayor retorno de todo el reporte.
2. `git init` + `.gitignore` + commit inicial (C2).
3. `/health` status real (C4).
4. `shutil.which` en el command runner del agente (M1a).
5. Deny-list de secretos en SafetyPolicy (M1b).
6. `web_fallback_used` en el toast del chat (M7a) + `persist` en chat-store (M7b).
7. Borrar `ollama_router_model` de settings o marcarlo "(futuro router LLM)".
8. Abort temprano de Vane sin fuentes (M5).
9. Dedup antes de embeber en ingesta (M4).

## 7. Mejoras de arquitectura

- El backend está bien; NO reescribir. Único refactor con retorno: extraer la construcción de
  clientes a singletons con `lru_cache` en `dependencies.py` (hoy cada request construye
  OllamaClient/ChromaClient/PerplexicaClient nuevos; Chroma es el caro).
- Sesiones del agente a persistencia simple (JSON en `backend/data/agent_sessions/`).
- Considerar `APIRouter` prefix `/api/v1` a futuro (no urgente, romperia frontend).

## 8. Rendimiento Ollama (medido hoy en TU hardware)

| Modelo | CPU medido | GPU medido | VRAM |
|---|---|---|---|
| llama3.2:3b | ~15-60s por respuesta corta | **98.2 tok/s** | 2.5 GB (completo) |
| qwen2.5:7b | 6.7 tok/s | **27.2 tok/s** | 4.2/5.1 GB (offload parcial) |
| bge-m3 embed | 1-30s bajo presión | sub-segundo | 1.2 GB |

Config recomendada (16 GB RAM + RTX 3060 6GB):
- `OLLAMA_MAX_LOADED_MODELS=2` (ya aplicado hoy) y pares por feature: chat = qwen2.5:7b+bge-m3,
  web = llama3.2+bge-m3. En VRAM caben llama3.2+bge juntos (3.7 GB); qwen7b solo con offload.
- `num_ctx`: 8192 para programación/BD/RAG (ya en skills), 4096 el resto. No subir a 32k (Vane lo
  pidió una vez y infló el modelo a 6.9 GB → swap).
- Embeddings: **bge-m3 para todo** (ya unificado; qwen3-embedding queda de repuesto). Mide antes
  de cambiarlo: el dataset de la sección 9 sirve de A/B.
- Modelfiles personalizados: **no necesarios** — las skills ya inyectan system+params por request;
  un Modelfile duplicaría eso y complica actualizar modelos.
- Medición continua: script `bench_ollama.ps1` que haga 1 generate por modelo y reporte
  `eval_count/eval_duration` + `size_vram` (te digo si estás en GPU o CPU en 10s).

## 9. Mejoras RAG + dataset de evaluación

Estrategia por tipo de documento:
- **UI/UX y Asistente** (guías cortas): chunk 1000/overlap 200 actual está bien.
- **Programación/Ciber (PDFs técnicos largos)**: subir chunk a ~1500 con overlap 250 al ingestarlos
  (menos chunks, más contexto por hit); ingestar por archivo con `limit_files` para no saturar.
- **Bases de datos (manuales de referencia)**: NO ingestar refman completo; extraer capítulos
  relevantes (el splitter no distingue secciones y el manual es 90% ruido para tus consultas).
- **PM² (docx/xlsx)**: hoy se ignoran en silencio — decidir soporte o documentar.

Dataset de 20 preguntas (correr con `POST /rag/query`, verificar fuente esperada y anotar
distancia del top-1 para calibrar el umbral):

| # | Pregunta | Colección | Fuente esperada |
|---|---|---|---|
| 1 | ¿Qué recetas de uso tengo para programación? | asistente | recetas_de_uso.md |
| 2 | ¿Cómo debo pedirle debugging al asistente? | asistente | guia_del_asistente.md |
| 3 | ¿Qué reglas de prompting para LLMs locales tengo? | programacion | prompting_llms_locales.md |
| 4 | ¿Qué buenas prácticas de desarrollo definí? | programacion | buenas_practicas_desarrollo.md |
| 5 | ¿Cómo estructurar un endpoint FastAPI según mis guías? | programacion | buenas_practicas_desarrollo.md |
| 6 | ¿Qué dice mi guía sobre índices en PostgreSQL? | bases_datos | postgresql_guia_practica.md |
| 7 | ¿Cómo hago EXPLAIN ANALYZE según mis documentos? | bases_datos | postgresql_guia_practica.md |
| 8 | ¿Qué fundamentos defensivos tengo documentados? | ciberseguridad | fundamentos_defensivos.md |
| 9 | ¿Qué dice mi material sobre logging defensivo? | ciberseguridad | fundamentos_defensivos.md |
| 10 | ¿Qué principios de contraste de color tengo? | ui_ux | principios_ui_ux_resumen.md |
| 11 | ¿Qué dice WCAG2 at a Glance sobre texto alternativo? | ui_ux | WCAG2-at-a-Glance.pdf |
| 12 | ¿Qué métodos de investigación de usuarios lista mi PDF? | ui_ux | User_Research_Methods_A4 |
| 13 | ¿Qué fases tiene el design thinking según mi material? | ui_ux | Innov_Team_Design-Thinking |
| 14 | ¿Qué guía de diseño móvil nativo tengo? | ui_ux | native_mobile_design_guide.pdf |
| 15 | Best practices de contenido para clientes, ¿qué cubren? | ui_ux | Best Practices Content Guide |
| 16-20 | 5 preguntas trampa (temas NO ingestados: Kubernetes, Rust, GraphQL, AWS, Kafka) | cada colección | **esperado: "no está en tus documentos"** — hoy fallarán (alucinación) hasta implementar M3 |

## 10-11. Skills/Router y Vane/SearXNG

(Detalle en M2 y M5. Resumen de decisiones:)
- **Cuándo RAG**: patrones explícitos (ya bien) + cuando la colección de la skill tenga hits bajo
  el umbral → propuesta: skills temáticas hacen mini-query RAG y añaden contexto si score bueno
  ("RAG contextual", hoy inexistente: las skills temáticas nunca citan tus documentos).
- **Cuándo web**: patrones de frescura (bien) + globo manual del composer (bien).
- **Cuándo directo**: resto. **Cuándo aclarar**: nunca lo hace hoy — añadir a los system prompts
  "si la petición es ambigua en un punto crítico, pregunta UNA aclaración antes de responder".
- **Vane**: mantener como primario con el abort temprano (M5); SearXNG de fallback está bien
  (los engines se suspenden ~3 min bajo rate-limit; es transitorio). Timeout actual 180s OK.

## 12. UI/UX

- Streaming (M6) — transformador.
- Persistir historial (M7) + lista de conversaciones (futuro).
- `/agent`: el diff viewer está bien; falta indicador de progreso durante plan/propose (hoy solo
  texto en el botón) y mostrar el árbol del workspace.
- Accesibilidad: los botones del composer tienen aria-labels ✓; falta `aria-live` para respuestas
  nuevas y focus management al abrir menús.
- Responsive OK (Playwright mobile pasa). Estados vacíos bien resueltos.
- Quick win visual: el topbar "updated HH:MM" no refresca solo (staleTime) — botón manual existe.

## 13. Modo agente: estado y plan "PRO" (tu petición)

**MVP actual** (verificado en vivo hoy): workspace confinado, plan LLM, diff aprobado, comandos
whitelisted, revert. **Lo que pediste** — darle una carpeta y que programe, descargue cosas y se
arme un entorno tipo Claude Code — es viable con este plan por fases (cada una aprobable por
separado):

- **A. Endurecer MVP** (los 4 fixes de M1) + git como red de seguridad (C2). ~1 sesión.
- **B. Bucle iterativo**: tras ejecutar un comando aprobado, el output vuelve al LLM que propone
  el siguiente paso (sigue siendo aprobar-cada-paso, pero el agente "ve" resultados y corrige).
  El plan además leerá el contenido de archivos clave (hoy solo ve el árbol). ~1-2 sesiones.
- **C. Entorno y dependencias**: whitelist ampliada con categorías aprobables:
  `python -m venv .venv`, `pip install <pkg>`, `npm install <pkg>`, `npm create`, y
  `git clone https://github.com/...` (solo dominios permitidos). "Descargar cosas" pasa SIEMPRE
  por gestores de paquetes o git — nunca curl arbitrario. Cada install requiere aprobación
  explícita como hoy. ~1 sesión.
- **D. Sesiones persistentes + git-rollback**: auto-branch al abrir sesión, commit por paso
  aprobado, rollback = git revert. Sustituye los backups en RAM. ~1 sesión.

Full-auto queda fuera por regla del proyecto (correcto: en 7B local el riesgo de prompt injection
y comandos erróneos es real; la aprobación es tu control).

## 14. Seguridad (global)

- CORS restringido a localhost ✓; backend escucha 127.0.0.1 ✓; sin auth (aceptable local-first,
  documentarlo); secretos: no hay .env real hoy, pero aplicar M1b antes de que exista.
- Vane container: puertos publicados en 0.0.0.0 (3000/4000) — cualquier dispositivo de tu red LAN
  puede usar tu SearXNG/Vane. Sugerencia: republicar como 127.0.0.1:3000:3000 en el run del
  contenedor.

## 15. Tests

Faltantes de mayor valor (en orden): integración de endpoints `/agent/*` con TestClient y LLM
fake; test del abort temprano de Vane; test de umbral RAG (mock de distancias); dataset RAG de la
sección 9 como script (`scripts/eval_rag.py`) con reporte de aciertos; Playwright: interacción de
envío de chat con backend mockeado (route interception). Los smoke de screenshots ya cubren
regresión visual básica + el nuevo test de menús.

## 16. Plan de implementación propuesto (espera tu aprobación)

| Fase | Contenido | Riesgo | Tiempo |
|---|---|---|---|
| F1 Quick wins | Sección 6 completa (9 ítems) | Mínimo | ~1 sesión |
| F2 RAG calidad | Umbral + get_collection + num_ctx + eval_rag.py + dataset | Bajo | ~1 sesión |
| F3 Streaming | `/chat/stream` + UI | Medio | 1-2 sesiones |
| F4 Agente A+B | Endurecer + bucle iterativo | Medio | 1-2 sesiones |
| F5 Agente C+D | Entorno/deps + git-rollback | Medio | 1-2 sesiones |
| F6 Router fino | Patrones + router LLM de 2ª pasada + RAG contextual en skills | Medio | ~1 sesión |

## 17. Archivos que se tocarían

F1: `scripts/check_all.ps1`, `scripts/run_all.ps1`, `.gitignore` (nuevo), `endpoints/health.py`,
`agent/safety_policy.py`, `agent/agent_service.py`, `settings.yaml`, `web_search_service.py`,
`perplexica_client.py`, `ingestion_service.py`, `chat-view.tsx`, `chat-store.ts`.
F2: `rag_service.py`, `chroma_client.py`, `scripts/eval_rag.py` (nuevo).
F3: `endpoints/chat.py`, `ollama_client.py`, `base_skill.py`, `lib/api/chat.ts`, `chat-view.tsx`.
F4-F5: módulo `agent/` + `agent-view.tsx`.
F6: `routing_rules.py`, `query_router.py`, skills.

## 18. Riesgos

- F3 toca el camino principal del chat → hacerlo aditivo (`/chat/stream` nuevo).
- F5 amplía superficie del agente → cada categoría de comando nueva pasa por tu aprobación de
  diseño primero.
- El bug de truncado de Cowork sigue existiendo → git (F1) es prerequisito de todo lo demás.

## 19. Comandos que puedes ejecutar tú para verificar

```powershell
# ¿Estoy en GPU o CPU? (si size_vram=0 → reiniciar Ollama)
Invoke-RestMethod http://localhost:11434/api/ps | ConvertTo-Json -Depth 4
nvidia-smi
# Velocidad real
ollama run llama3.2 --verbose "di hola"
# Estado servicios
Invoke-RestMethod http://127.0.0.1:8000/health | ConvertTo-Json -Depth 5
```

## 20. Recomendación final

Aprueba **F1 (quick wins) ya** — es una sesión, riesgo mínimo, e incluye los dos fixes que más
cambian tu día a día (watchdog GPU + git). Después F2/F3 (calidad RAG + streaming) que es donde
más se siente la mejora al usarlo. El plan del agente PRO (F4-F5) está diseñado para crecer sin
romper la regla de oro: **nada se ejecuta sin tu aprobación**.
