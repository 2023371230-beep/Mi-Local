# FINAL_VANE_WEB_REPORT

Estado: 🟢 confiable con fallback. Búsqueda web de ~4 min → ~1:15.

## Diagnóstico (causa de los timeouts históricos)
Tres problemas apilados, todos resueltos:
1. `OLLAMA_MAX_LOADED_MODELS=1` → thrashing intra-request (chat→embed→chat recargaba modelos).
   Fix: =2 + pares de modelos que caben juntos.
2. **`stream:false` de Vane cuelga para siempre** (bug del fork, verificado en su route.js).
   Fix: cliente consume SIEMPRE el stream NDJSON (init/sources/response/done).
3. Engines de SearXNG suspendidos por rate-limit → Vane alucina sin fuentes. Fix: el servicio
   exige answer+sources y descarta lo demás.

## Arquitectura de búsqueda
```
/web/search → PerplexicaClient.search (streaming)
   ├─ emite 'sources' antes del 1er token → OK, sintetiza Vane
   └─ 1er token sin 'sources' → ABORT temprano (ahorra 1-2 min)
      → WebSearchService fallback → SearXNG /search?format=json
         → síntesis con llama3.2 (98 tok/s) citando URLs
```

## /health (estado real)
`web_search.status`: ok (vane sin errores) | degraded (uno de los dos) | error (ninguno).
Campos: engine, providers_endpoint, search_endpoint, fallback_available, last_error.
El frontend muestra fallback vía `web_fallback_used` (toast) — ya no por heurística de source.

## Config
- `vane_chat_model: llama3.2` + `vane_embed_model: bge-m3` (caben juntos en VRAM).
- `vane_search_timeout: 180`. Fallback SearXNG timeout 15s.

## Recomendación
Vane primario funciona pero depende de que su SearXNG interno tenga resultados (rate-limit ~3min).
El fallback SearXNG externo (:4000) es sólido. Si Vane molesta, se puede invertir el orden en
`web_search_service` sin tocar nada más. Verificado en vivo: "OWASP Top 10 2025" y "NIST CSF 2.0"
→ respuestas correctas en español con 5 fuentes reales.
