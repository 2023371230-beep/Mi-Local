# ARCHITECTURE — Modelo IA Carrera

## Vista general

```
┌─────────────┐   HTTP    ┌──────────────────────────┐   HTTP   ┌────────────┐
│  Frontend   │ ────────► │  Backend FastAPI :8000    │ ───────► │  Ollama    │
│ Next.js 16  │ ◄──────── │  (clean architecture)     │ ◄─────── │  :11434    │
│  :3001      │  NDJSON   │                           │          │ (RTX 3060) │
└─────────────┘           │  ├─ presentation (API)    │          └────────────┘
                          │  ├─ application (skills,  │   embed/query
                          │  │   router, services,    │ ─────────► ChromaDB
                          │  │   agent, documents)     │           (local, disk)
                          │  ├─ domain (schemas,      │
                          │  │   interfaces, models)   │   HTTP
                          │  └─ infrastructure        │ ─────────► Vane :3000
                          │      (ollama, chroma,     │           SearXNG :4000
                          │       web, parsers, docs) │           (Docker)
                          └──────────────────────────┘
```

## Backend — clean architecture (backend/app/)

- **presentation/**: endpoints FastAPI + `dependencies.py` (inyección) + `main.py` (app factory,
  CORS localhost, handler global de errores). Un router por área: chat, health, models, ingest,
  rag, web_search, logs, agent, documents.
- **application/**: lógica de negocio.
  - `router/`: QueryRouter (regex → skill+modelo) + routing_rules.
  - `services/`: chat, rag, web_search, ingestion, model, document.
  - `skills/`: base_skill (few-shot + chat_options) + 7 skills temáticas.
  - `agent/`: safety_policy (límites duros) + agent_service (plan/diff/apply/memoria).
- **domain/**: schemas Pydantic, interfaces (LLMClient, VectorDB…), models.
- **infrastructure/**: ollama_client, chroma_client, web (perplexica/searxng),
  parsers (pdf, text_splitter), documents (html/docx/pdf/md_blocks), logging.

## Flujos clave

**Chat**: request → QueryRouter elige skill+modelo → skill construye mensajes (system + few-shot
+ user) → OllamaClient.chat[_stream] → respuesta. `/chat` síncrono, `/chat/stream` NDJSON.

**RAG**: pregunta → embed (bge-m3) → ChromaDB.query top_k → filtro por umbral distancia
(rag_max_distance) → si nada relevante, se rechaza; si sí, contexto → LLM cita fuentes.

**Web search**: Vane `/api/search` (streaming) → si emite `sources` sigue; si el primer token
llega sin sources, aborta → fallback SearXNG `/search?format=json` → síntesis con llama3.2.

**Agente**: create_session (workspace confinado) → propose_plan (LLM coder → JSON validado) →
propose_edit (diff, no escribe) → apply_step(approved=True) (backup + escribe + actions.log).
Nada se escribe/ejecuta sin `approved=True`.

**Documentos**: tipo+título+indicaciones (+RAG opcional) → LLM genera Markdown → generador por
formato (md/html/docx/pdf) → outputs/ → descarga.

## Frontend (frontend/)

- `app/`: rutas (chat, rag, documents, agent, models, logs, skills, settings, dashboard).
- `components/`: layout (app-shell, sidebar con toggle simple/pro, top-bar, right-panel),
  chat, rag, documents, agent, ui (shadcn/base-ui).
- `lib/`: api clients (fetch + Zod), stores (zustand persist: chat-history, ui), types, config.
- Estado: TanStack Query (server) + Zustand (cliente). Motion para microinteracciones.

## Puertos

| Puerto | Servicio |
|---|---|
| 8000 | Backend FastAPI |
| 3001 | Frontend Next.js (dev) |
| 3000 | Vane (contenedor) |
| 4000 | SearXNG interno de Vane |
| 11434 | Ollama |

## Decisiones de arquitectura
Ver `DECISIONS.md`. Resumen: local-first, sin APIs de pago, clean architecture en backend,
agente nunca full-auto, embeddings unificados en bge-m3, Vane solo por streaming.
