from __future__ import annotations

from loguru import logger

from app.config import Settings
from app.domain.interfaces import LLMClient
from app.infrastructure.web.perplexica_client import PerplexicaClient
from app.infrastructure.web.searxng_client import SearxngClient


class WebSearchService:
    """Orquesta la busqueda web: intenta Vane, cae a SearXNG + sintesis con Ollama.

    Contrato de respuesta:
    - engine: "vane" | "searxng" | "none"
    - fallback_used: True si respondio SearXNG por fallo de Vane
    - vane_error: el error de Vane aunque el fallback haya funcionado
    - error: None si hubo respuesta valida (aunque sea por fallback)
    """

    def __init__(
        self,
        settings: Settings,
        llm_client: LLMClient,
        perplexica_client: PerplexicaClient,
        searxng_client: SearxngClient,
    ) -> None:
        self.settings = settings
        self.llm_client = llm_client
        self.perplexica_client = perplexica_client
        self.searxng_client = searxng_client

    def health(self) -> bool:
        return self.perplexica_client.health() or self.searxng_client.health()

    def status(self) -> dict:
        """Estado real para /health: ok | degraded | error."""
        vane_ok = self.perplexica_client.health()
        searxng_ok = self.searxng_client.health()
        if vane_ok and not PerplexicaClient.last_error:
            status = "ok"
        elif vane_ok or searxng_ok:
            status = "degraded"
        else:
            status = "error"
        return {
            "status": status,
            "primary": "vane",
            "fallback": "searxng",
            "vane_available": vane_ok,
            "fallback_available": searxng_ok,
            "last_error": PerplexicaClient.last_error,
        }

    def search_and_answer(
        self,
        query: str,
        limit: int = 5,
        sources: list[str] | None = None,
        optimization_mode: str | None = None,
    ) -> dict:
        vane_result = self.perplexica_client.search(
            query,
            optimization_mode=optimization_mode,
            sources=sources or ["web"],
        )
        if vane_result.get("answer") and vane_result.get("sources"):
            return {
                "answer": vane_result["answer"],
                "web_used": True,
                "engine": "vane",
                "fallback_used": False,
                "vane_error": None,
                "sources": vane_result["sources"][:limit],
                "error": None,
            }

        vane_error = vane_result.get("error") or "Vane returned an empty answer."
        logger.warning("Vane fallo, intentando fallback SearXNG: {}", vane_error)

        results = self.searxng_client.search(query, limit=limit)
        if not results:
            return {
                "answer": "",
                "web_used": False,
                "engine": "none",
                "fallback_used": False,
                "vane_error": vane_error,
                "sources": [],
                "error": "No web engine available",
            }

        answer = self._synthesize(query, results)
        return {
            "answer": answer,
            "web_used": True,
            "engine": "searxng",
            "fallback_used": True,
            "vane_error": vane_error,
            "sources": results,
            "error": None,
        }

    def _synthesize(self, query: str, results: list[dict]) -> str:
        context = "\n".join(
            f"[{idx}] {item.get('title')} - {item.get('url')}\n{item.get('content')}"
            for idx, item in enumerate(results, start=1)
        )
        try:
            return self.llm_client.chat(
                self.settings.ollama_general_model,
                [
                    {"role": "system", "content": "Sintetiza resultados web y cita URLs. Si hay incertidumbre, dilo."},
                    {"role": "user", "content": f"Pregunta: {query}\n\nResultados:\n{context}"},
                ],
                options={"temperature": 0.1, "num_ctx": 4096},
            )
        except Exception as exc:  # noqa: BLE001 - la sintesis nunca debe tumbar la busqueda
            logger.warning("Sintesis con Ollama fallo, devolviendo snippets crudos: {}", exc)
            return "\n\n".join(
                f"{item.get('title')}\n{item.get('url')}\n{item.get('content')}" for item in results
            )
