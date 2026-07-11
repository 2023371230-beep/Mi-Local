from __future__ import annotations

import json
import re
import time
from typing import Any

import httpx
from loguru import logger

_OLLAMA_TAG_PATTERN = re.compile(r"^[\w.\-]+:[\w.\-]+$")


class PerplexicaClient:
    """Cliente robusto para Vane (Perplexica).

    - Detecta el provider Ollama por nombre, id, baseUrl o forma de los modelos.
    - Cachea /api/providers con TTL para no sumar latencia a cada busqueda.
    - Usa timeouts separados para providers (rapido) y search (largo).
    - Nunca lanza: siempre devuelve un dict con "error" controlado.
    - Expone el ultimo error en `last_error` para /health.
    """

    last_error: str | None = None

    def __init__(
        self,
        base_url: str,
        timeout: float = 60.0,
        chat_model: str = "qwen2.5:7b",
        embed_model: str = "qwen3-embedding:0.6b",
        fallback_embed_model: str = "bge-m3",
        optimization_mode: str = "speed",
        providers_timeout: float = 10.0,
        providers_cache_ttl: float = 60.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.chat_model = chat_model
        self.embed_model = embed_model
        self.fallback_embed_model = fallback_embed_model
        self.optimization_mode = optimization_mode
        self.providers_timeout = providers_timeout
        self.providers_cache_ttl = providers_cache_ttl
        self._providers_cache: list[dict[str, Any]] | None = None
        self._providers_cache_at: float = 0.0

    # ------------------------------------------------------------------ health

    def health(self) -> bool:
        try:
            response = httpx.get(f"{self.base_url}/api/providers", timeout=3.0)
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    # --------------------------------------------------------------- providers

    def get_providers(self, use_cache: bool = True) -> list[dict[str, Any]]:
        now = time.monotonic()
        if use_cache and self._providers_cache is not None and (now - self._providers_cache_at) < self.providers_cache_ttl:
            return self._providers_cache
        try:
            response = httpx.get(f"{self.base_url}/api/providers", timeout=self.providers_timeout)
            response.raise_for_status()
            payload = response.json()
        except httpx.HTTPError as exc:
            PerplexicaClient.last_error = f"Vane providers request failed: {exc}"
            logger.warning("Vane providers request failed: {}", exc)
            return []
        providers = payload.get("providers", []) if isinstance(payload, dict) else []
        if not isinstance(providers, list):
            providers = []
        self._providers_cache = providers
        self._providers_cache_at = now
        return providers

    def providers(self) -> list[dict[str, Any]]:
        return self.get_providers()

    # -------------------------------------------------------- provider matching

    def find_ollama_provider(self, providers: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
        providers = providers if providers is not None else self.get_providers()
        # 1) match directo por texto en name/id/baseUrl
        for provider in providers:
            haystack = " ".join(
                str(provider.get(key, "")) for key in ("name", "id", "baseUrl", "base_url", "url")
            ).lower()
            if any(token in haystack for token in ("ollama", "11434", "host.docker.internal")):
                return provider
        # 2) provider que contenga exactamente el chat model configurado
        for provider in providers:
            keys = self._model_keys(provider.get("chatModels", []))
            if self.chat_model in keys:
                return provider
        # 3) provider cuyos modelos tengan forma de tag Ollama ("modelo:tag")
        for provider in providers:
            keys = self._model_keys(provider.get("chatModels", []))
            if keys and all(_OLLAMA_TAG_PATTERN.match(key) for key in keys):
                return provider
        return None

    def detect_ollama_provider(self) -> dict[str, Any] | None:
        return self.find_ollama_provider()

    def detect_model(self, provider: dict[str, Any], preferred_names: list[str], kind: str = "chat") -> str | None:
        models = provider.get("chatModels" if kind == "chat" else "embeddingModels", [])
        return self._pick_model(models, preferred_names)

    def find_chat_model(self, provider: dict[str, Any], preferred: list[str] | None = None) -> str | None:
        preferred = preferred or [self.chat_model, "qwen2.5:7b", "llama3.2:latest"]
        return self._pick_model(provider.get("chatModels", []), preferred)

    def find_embedding_model(self, provider: dict[str, Any], preferred: list[str] | None = None) -> str | None:
        preferred = preferred or [
            self.embed_model,
            "qwen3-embedding:0.6b",
            self.fallback_embed_model,
            "bge-m3",
            "nomic-embed-text",
        ]
        return self._pick_model(provider.get("embeddingModels", []), preferred)

    # ------------------------------------------------------------------ search

    def build_search_payload(
        self,
        query: str,
        provider: dict[str, Any],
        chat_model: str,
        embedding_model: str,
        history: list[list[str]] | None = None,
        optimization_mode: str | None = None,
        sources: list[str] | None = None,
        system_instructions: str | None = None,
    ) -> dict[str, Any]:
        return {
            "chatModel": {"providerId": provider["id"], "key": chat_model},
            "embeddingModel": {"providerId": provider["id"], "key": embedding_model},
            "optimizationMode": optimization_mode or self.optimization_mode,
            "sources": sources or ["web"],
            "query": query,
            "history": history or [],
            "systemInstructions": system_instructions or "Answer briefly and include sources.",
            # El modo no-streaming de Vane nunca cierra la respuesta (cuelga
            # indefinido aunque la sintesis termine); siempre se usa stream.
            "stream": True,
        }

    def _post_search(self, payload: dict[str, Any], timeout: float) -> dict[str, Any]:
        """Consume el stream NDJSON de /api/search y ensambla la respuesta.

        Vane emite 'sources' ANTES del primer token de respuesta. Si llega un
        'response' sin sources previos, su SearXNG interno dio 0 resultados y la
        respuesta seria alucinada: se aborta ahi mismo para saltar al fallback
        sin esperar 1-2 minutos de generacion inutil.
        """
        request_timeout = httpx.Timeout(timeout, connect=min(10.0, timeout))
        answer_parts: list[str] = []
        sources: list[dict[str, Any]] = []
        stream_error: str | None = None
        aborted_no_sources = False
        with httpx.stream(
            "POST", f"{self.base_url}/api/search", json=payload, timeout=request_timeout
        ) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                line = (line or "").strip()
                if line.startswith("data:"):
                    line = line[5:].strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                event_type = event.get("type")
                if event_type == "response":
                    if not sources and not answer_parts:
                        aborted_no_sources = True
                        break
                    answer_parts.append(str(event.get("data") or ""))
                elif event_type == "sources":
                    data = event.get("data")
                    if isinstance(data, list):
                        sources = data
                elif event_type == "error":
                    stream_error = str(event.get("data") or "unknown stream error")
                    break
                elif event_type in ("done", "end"):
                    break
        if aborted_no_sources:
            return {"message": "", "sources": [], "error": None, "no_sources": True}
        result: dict[str, Any] = {"message": "".join(answer_parts), "sources": sources}
        if stream_error:
            result["error"] = stream_error
        return result

    def search(
        self,
        query: str,
        history: list[list[str]] | None = None,
        optimization_mode: str | None = None,
        sources: list[str] | None = None,
        system_instructions: str | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        providers = self.get_providers()
        if not providers:
            return self._error("Vane is not available or /api/providers returned no providers.")
        provider = self.find_ollama_provider(providers)
        if not provider:
            names = [str(item.get("name", "?")) for item in providers]
            return self._error(f"Vane is available but no Ollama provider was found. Providers: {names}")

        chat_model = self.find_chat_model(provider)
        embedding_model = self.find_embedding_model(provider)
        if not chat_model or not embedding_model:
            return self._error("Vane Ollama provider is missing the required chat or embedding model.")

        payload = self.build_search_payload(
            query,
            provider,
            chat_model,
            embedding_model,
            history=history,
            optimization_mode=optimization_mode,
            sources=sources,
            system_instructions=system_instructions,
        )
        effective_timeout = timeout or self.timeout
        logger.info(
            "Vane search provider={} chat_model={} embed_model={} timeout={}s",
            provider.get("name", provider.get("id", "?")),
            chat_model,
            embedding_model,
            effective_timeout,
        )
        started = time.perf