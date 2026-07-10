from __future__ import annotations

from typing import Any

import httpx

from app.domain.interfaces import LLMClient


class OllamaClient(LLMClient):
    def __init__(self, base_url: str, timeout: float = 120.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def health(self) -> bool:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    def list_models(self) -> list[dict[str, Any]]:
        try:
            response = httpx.get(f"{self.base_url}/api/tags", timeout=10.0)
            response.raise_for_status()
            return response.json().get("models", [])
        except httpx.HTTPError:
            return []

    def chat(self, model: str, messages: list[dict[str, str]], options: dict[str, Any] | None = None) -> str:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            "keep_alive": 0,
        }
        if options:
            payload["options"] = options

        try:
            response = httpx.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            return data.get("message", {}).get("content", "")
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Ollama chat failed for model {model}: {exc}") from exc

    def embed(self, model: str, text: str) -> list[float]:
        payload = {"model": model, "input": text, "keep_alive": 0}
        try:
            response = httpx.post(
                f"{self.base_url}/api/embed",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()
            embeddings = data.get("embeddings") or []
            if embeddings and isinstance(embeddings[0], list):
                return embeddings[0]
            return data.get("embedding", [])
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Ollama embedding failed for model {model}: {exc}") from exc
