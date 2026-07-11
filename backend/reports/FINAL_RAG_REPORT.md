# FINAL_RAG_REPORT

Estado: 🟢 calibrado y evaluado. 20/20 en el dataset de prueba.

## Configuración
- Embeddings: **bge-m3** para todo (unificado con Vane para no intercambiar modelos).
- Chunking: 1000 chars / 200 overlap, con frontera suave (corta en `. `/`; `/`: `/espacio).
- Métrica: L2² de Chroma (default). Umbral `rag_max_distance=1.03`.
- Dedup: por hash SHA-256 del chunk, ANTES de embeber (re-ingesta gratis si no cambió).

## Colecciones (bge-m3)
| Colección | Chunks | Fuentes |
|---|---|---|
| asistente | 7 | guia_del_asistente.md, recetas_de_uso.md |
| programacion | 8 | buenas_practicas, prompting_llms_locales |
| bases_datos | 5 | postgresql_guia_practica |
| ciberseguridad | 5 | fundamentos_defensivos |
| ui_ux | 78 | principios + 5 PDFs (WCAG, User Research, Design Thinking, mobile, content) |

## Evaluación (scripts/eval_rag.py, en vivo 2026-07-10)
- 15/15 preguntas reales: fuente esperada en top-3.
- 5/5 trampas (Kubernetes, Rust, AWS, Kafka, GraphQL): correctamente rechazadas.
- Distancias: hits reales 0.67–1.00, ruido 1.07–1.28 → umbral 1.03 los separa limpio.

## Anti-alucinación
`rag_service.answer` filtra por umbral; si nada pasa, responde "no encontré nada relevante
(mejor distancia: X)" en vez de pasar ruido al modelo. Test: `test_rag_answer_rejects_low_relevance`.

## Huecos / pendiente
- PDFs grandes (refman MySQL/PostgreSQL, JLS, specs) NO ingestados a propósito (horas de CPU;
  ahora con dedup barato se pueden ingestar por lote cuando se necesiten).
- PM² (docx/xlsx) no soportado por el parser (solo PDF/MD/TXT) — decidir python-docx o documentar.
- Sin reranking cross-encoder (no viable en 16GB); el umbral + orden por distancia alcanza.
- RAG contextual en skills temáticas (que citen documentos sin pedirlo explícito): pendiente F6.
