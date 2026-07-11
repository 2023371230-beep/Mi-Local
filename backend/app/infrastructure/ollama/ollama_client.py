from __future__ import annotations

import json
from typing import Any, Iterator

import httpx

from app.domain.interfaces import LLMClient

# keep_alive=0 descargaba el modelo tras CADA peticion (recarga completa de 5-60s
# en el siguiente turno). Se mantienen residentes; Ollama igual desaloja por memoria.
_CHAT_KEEP_ALIVE = "30m"
_EMBED_KEEP_ALIVE = "60m"


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
            "keep_alive": _CHAT_KEEP_ALIVE,
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

    def chat_stream(
        self, model: str, messages: list[dict[str, str]], options: dict[str, Any] | None = None
    ) -> Iterator[str]:
        """Genera la respuesta token a token (para /chat/stream)."""
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": True,
            "keep_alive": _CHAT_KEEP_ALIVE,
        }
        if options:
            payload["options"] = options
        try:
            with httpx.stream(
                "POST", f"{self.base_url}/api/chat", json=payload, timeout=self.timeout
            ) as response:
                response.raise_for_status()
                for line in response.iter_lines():
                    if not line:
                        continue
                    try:
                        event = json.loads(line)
                    except ValueError:
                        continue
                    chunk = event.get("message", {}).get("content", "")
                    if chunk:
                        yield chunk
                    if event.get("done"):
                        break
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Ollama chat stream failed for model {model}: {exc}") from exc

    def embed_batch(self, model: str, texts: list[str]) -> list[list[float]]:
        """Embebe varios textos en UNA peticion (amortiza HTTP/cola; clave en ingestas)."""
        if not texts:
            return []
        payload = {"model": model, "input": texts, "keep_alive": _EMBED_KEEP_ALIVE}
        try:
            response = httpx.post(f"{self.base_url}/api/embed", json=payload, timeout=self.timeout)
            response.raise_for_status()
            embeddings = response.json().get("embeddings") or []
            if len(embeddings) != len(texts):
                raise RuntimeError(
                    f"Ollama devolvio {len(embeddings)} embeddings para {len(texts)} textos"
                )
            return embeddings
        except httpx.HTTPError as exc:
            raise RuntimeError(f"Ollama batch embedding failed for model {model}: {exc}") from exc

    def embed(self, model: str, text: str) -> list[float]:
        payload = {"model": model, "input": text, "keep_alive": _EMBED_KEEP_ALIVE}
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
