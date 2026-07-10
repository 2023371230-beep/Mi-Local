"""Debug manual de Vane (Perplexica).

Uso:
    cd backend
    .\\.venv\\Scripts\\Activate.ps1
    python .\\scripts\\debug_vane_search.py [query]

Consulta /api/providers, detecta el provider Ollama y los modelos,
ejecuta /api/search con timeout largo e imprime el resultado completo.
"""

from __future__ import annotations

import json
import sys
import time

import httpx

VANE_URL = "http://localhost:3000"
CHAT_MODEL = "llama3.2:latest"
EMBED_MODEL = "bge-m3"
FALLBACK_EMBED = "qwen3-embedding:0.6b"
TIMEOUT = 240.0


def main() -> int:
    query = sys.argv[1] if len(sys.argv) > 1 else "What is OWASP?"

    # 1. Providers
    print(f"== GET {VANE_URL}/api/providers")
    try:
        response = httpx.get(f"{VANE_URL}/api/providers", timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        print(f"ERROR: providers no responde: {exc}")
        print("¿Esta corriendo el contenedor? -> docker ps ; docker logs vane --tail 100")
        return 1

    payload = response.json()
    print(json.dumps(payload, indent=2, ensure_ascii=False)[:3000])
    providers = payload.get("providers", [])

    # 2. Detectar provider Ollama
    provider = None
    for item in providers:
        haystack = " ".join(str(item.get(k, "")) for k in ("name", "id", "baseUrl", "url")).lower()
        if any(tok in haystack for tok in ("ollama", "11434", "host.docker.internal")):
            provider = item
            break
    if provider is None and providers:
        provider = providers[0]
        print("AVISO: no se detecto provider Ollama por nombre; usando el primero.")
    if provider is None:
        print("ERROR: Vane no tiene providers configurados.")
        return 1

    print(f"\nProvider: id={provider.get('id')} name={provider.get('name')}")

    def pick(models: list[dict], preferred: list[str]) -> str | None:
        keys = [m.get("key") for m in models or [] if m.get("key")]
        for want in preferred:
            for key in keys:
                if want == key or want in key:
                    return key
        return keys[0] if keys else None

    chat_model = pick(provider.get("chatModels", []), [CHAT_MODEL])
    embed_model = pick(provider.get("embeddingModels", []), [EMBED_MODEL, FALLBACK_EMBED])
    print(f"Chat model:  {chat_model}")
    print(f"Embed model: {embed_model}")
    if not chat_model or not embed_model:
        print("ERROR: faltan modelos chat/embedding en el provider. Revisar config de Vane.")
        return 1

    # 3. Search (streaming: el modo no-streaming de Vane cuelga indefinidamente)
    body = {
        "chatModel": {"providerId": provider["id"], "key": chat_model},
        "embeddingModel": {"providerId": provider["id"], "key": embed_model},
        "optimizationMode": "speed",
        "sources": ["web"],
        "query": query,
        "history": [],
        "systemInstructions": "Answer briefly with sources.",
        "stream": True,
    }
    print(f"\n== POST {VANE_URL}/api/search (stream)  query={query!r}  timeout={TIMEOUT}s")
    started = time.perf_counter()
    answer_parts: list[str] = []
    sources: list[dict] = []
    try:
        with httpx.stream("POST", f"{VANE_URL}/api/search", json=body, timeout=TIMEOUT) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                line = (line or "").strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                etype = event.get("type")
                if etype == "init":
                    print(f"  init a los {time.perf_counter() - started:.1f}s")
                elif etype == "sources":
                    sources = event.get("data") or []
                    print(f"  sources ({len(sources)}) a los {time.perf_counter() - started:.1f}s")
                elif etype == "response":
                    if not answer_parts:
                        print(f"  primer token a los {time.perf_counter() - started:.1f}s")
                    answer_parts.append(str(event.get("data") or ""))
                elif etype in ("done", "end"):
                    break
                elif etype == "error":
                    print(f"ERROR en stream: {event.get('data')}")
                    return 1
    except httpx.TimeoutException:
        print(f"ERROR: timeout tras {TIMEOUT}s.")
        print("Causa probable: Ollama lento (carga de modelo) o cola ocupada (OLLAMA_NUM_PARALLEL=1).")
        print("Revisar: curl http://localhost:11434/api/ps ; docker logs vane --tail 50")
        return 1
    except httpx.HTTPError as exc:
        print(f"ERROR: {exc}")
        return 1

    elapsed = time.perf_counter() - started
    print(f"tiempo total={elapsed:.1f}s")
    answer = "".join(answer_parts)
    if not sources:
        print("AVISO: Vane no emitio sources -> su SearXNG interno dio 0 resultados;")
        print("la respuesta puede ser alucinada. El backend la descarta y usa el fallback SearXNG.")
    print(f"\nANSWER ({len(answer)} chars):\n{answer[:1200]}")
    print(f"\nSOURCES ({len(sources)}):")
    for src in sources[:5]:
        meta = src.get("metadata", {}) or {}
        print(f"  - {meta.get('title', '?')} | {meta.get('url', '?')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
