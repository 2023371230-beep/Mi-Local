# OLLAMA_OPTIMIZATION_REPORT

Mediciones reales en la laptop del usuario (Ryzen 9 5900HX, 16 GB, RTX 3060 Laptop 6GB), 2026-07-10.

## Hallazgo principal: GPU intermitente
La RTX 3060 funciona (nvidia-smi ok, CUDA 13.1) pero la detección de Ollama falla tras suspender
la laptop y cae a CPU **en silencio**. Impacto medido:

| Modelo | CPU | GPU | Factor |
|---|---|---|---|
| llama3.2:3b | ~7 tok/s | **98.2 tok/s** | 14× |
| qwen2.5:7b | 6.7 tok/s | **27.2 tok/s** | 4× |
| bge-m3 embed | 1-30s | sub-segundo | — |

Mitigación: `scripts/check_gpu.ps1 -Fix` (integrado en run_all/check_all) genera 1 token, lee
`size_vram` de /api/ps y reinicia Ollama si es 0.

## Configuración recomendada (aplicada)
- `OLLAMA_MAX_LOADED_MODELS=2`: con 1 hay thrashing intra-request; con 3 hay swapping.
- `OLLAMA_NUM_PARALLEL=1`: cola única (una petición pesada a la vez es lo sano en esta RAM).
- keep_alive: 30m chat / 60m embeddings (antes 0 → recarga completa tras cada request).
- Pares que coexisten en 6GB VRAM: llama3.2 (2.5GB) + bge-m3 (1.2GB). qwen2.5:7b (4.2GB) entra
  con offload parcial; no cabe junto a otro 7B.

## Modelo por tarea
| Tarea | Modelo | Razón |
|---|---|---|
| chat general, RAG, documentos | qwen2.5:7b | mejor calidad de prosa/razonamiento |
| programación, BD, agente | qwen2.5-coder:7b | código |
| síntesis búsqueda web | llama3.2 | rápido (98 tok/s), cabe completo en VRAM |
| embeddings (todo) | bge-m3 | unificado; evita intercambio de modelos |

## Contexto (num_ctx)
- 8192: programación, BD, RAG, documentos (prompts con contexto largo).
- 4096: chat general, ciberseguridad, UI (respuestas más cortas).
- No subir a 32k: infla el modelo y provoca swap (Vane lo pidió una vez → 6.9GB).

## Embeddings: bge-m3 vs qwen3-embedding
bge-m3 elegido para todo. Razón práctica: tener UN solo modelo de embeddings residente evita que
Ollama desaloje modelos al alternar RAG↔web. qwen3-embedding:0.6b queda de repuesto/fallback.
No se midió diferencia de calidad de retrieval que justifique el costo de mantener dos.

## Router: ¿llama3.2 sirve?
Hoy el router es 100% regex (0 latencia). llama3.2 está reservado para una 2ª pasada (cuando
ninguna regex matchee) — a 98 tok/s sería ~1s, viable. Pendiente F6.

## Cómo medir (repetible)
```powershell
# GPU sí/no
Invoke-RestMethod http://localhost:11434/api/ps | ConvertTo-Json -Depth 4
# tok/s
ollama run llama3.2 --verbose "di hola"
```
El backend loguea `latency_ms` por request de chat en backend/logs/backend.log.
