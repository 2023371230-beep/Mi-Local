# DECISIONS — registro de decisiones técnicas

Formato: fecha — decisión — por qué — alternativa descartada.

- 2026-07-10 — **Vane siempre por streaming NDJSON** — su modo no-streaming nunca cierra la
  respuesta (verificado en el código del fork) — esperar el fix upstream.
- 2026-07-10 — **Abort temprano si Vane no emite `sources`** — sources llega antes del primer
  token; sin sources la respuesta es alucinada y se descartaría igual; ahorra 1-2 min —
  esperar la generación completa.
- 2026-07-10 — **Embeddings unificados en bge-m3 (RAG + Vane)** — un solo modelo residente
  evita el intercambio de modelos en 16 GB; qwen3-embedding queda de repuesto — mantener dos
  modelos de embeddings distintos.
- 2026-07-10 — **OLLAMA_MAX_LOADED_MODELS=2** — con 1 hay thrashing intra-request; con 3 hay
  swapping (medido) — 1 o 3.
- 2026-07-10 — **Watchdog GPU en scripts** (check_gpu.ps1) — la detección CUDA de Ollama falla
  intermitentemente tras suspender y cae a CPU en silencio (7 vs 98 tok/s medidos) — confiar en
  que Ollama siempre detecta.
- 2026-07-10 — **Umbral RAG rag_max_distance=1.03 (L2² Chroma)** — calibrado en vivo: hits
  reales 0.67-1.00, ruido ≥1.07; 20/20 en eval_rag.py — umbral por coseno teórico (0.75 rechazaba
  hits reales).
- 2026-07-10 — **Few-shot + chat_options por skill en vez de Modelfiles** — las skills ya
  inyectan system/params por request; Modelfiles duplicarían config — crear modelos Ollama custom.
- 2026-07-10 — **Agente: aprobación explícita SIEMPRE, sin full-auto** — 7B local con prompt
  injection posible desde archivos; el humano es el control — modo autónomo.
- 2026-07-10 — **Router sigue siendo regex; llama3.2 reservado para 2ª pasada (F6)** — el regex
  cubre lo común y llama3.2 a 98 tok/s hará viable la 2ª pasada — router LLM para todo (latencia).
- 2026-07-10 — **git init con baseline previo a F1** — red de seguridad ante el bug de truncado
  de Cowork y las escrituras del agente — seguir sin control de versiones.
