from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import get_settings


def pick_provider(providers: list[dict[str, Any]]) -> dict[str, Any] | None:
    for provider in providers:
        name = str(provider.get("name", "")).lower()
        if "ollama" in name or "11434" in name or "host.docker.internal" in name:
            return provider
    return None


def pick_model(models: list[dict[str, Any]], preferred: list[str]) -> str | None:
    keys = [model.get("key") for model in models if model.get("key")]
    for wanted in preferred:
        if wanted in keys:
            return wanted
    return keys[0] if keys else None


def main() -> int:
    settings = get_settings()
    base_url = settings.perplexica_url.rstrip("/")

    try:
        providers_response = httpx.get(f"{base_url}/api/providers", timeout=15.0)
        providers_response.raise_for_status()
        providers = providers_response.json().get("providers", [])
    except Exception as exc:
        print(f"providers failed: {exc}")
        return 1

    provider = pick_provider(providers)
    if not provider:
        print("No Ollama provider found.")
        print(json.dumps(providers, indent=2))
        return 1

    chat_model = pick_model(provider.get("chatModels", []), [settings.vane_chat_model, settings.ollama_general_model])
    embed_model = pick_model(provider.get("embeddingModels", []), [settings.vane_embed_model, settings.ollama_embed_model, "nomic-embed-text"])
    if not chat_model or not embed_model:
        print("Required models were not found.")
        print(json.dumps(provider, indent=2))
        return 1

    payload = {
        "chatModel": {"providerId": provider["id"], "key": chat_model},
        "embeddingModel": {"providerId": provider["id"], "key": embed_model},
        "optimizationMode": settings.vane_optimization_mode,
        "sources": ["web"],
        "query": "What is OWASP Top 10?",
        "history": [],
        "systemInstructions": "Answer briefly and include sources.",
        "stream": False,
    }

    try:
        search_response = httpx.post(f"{base_url}/api/search", json=payload, timeout=180.0)
        search_response.raise_for_status()
        data = search_response.json()
    except Exception as exc:
        print(f"search failed: {exc}")
        return 1

    print("provider=" + provider["name"])
    print("chat_model=" + chat_model)
    print("embedding_model=" + embed_model)
    print("message=" + str(data.get("message") or data.get("answer") or "")[:1000])
    print("sources=" + json.dumps(data.get("sources", []), indent=2)[:2000])
    return 0 if data.get("message") or data.get("answer") else 1


if __name__ == "__main__":
    raise SystemExit(main())
