from __future__ import annotations

import httpx
from fastapi import Depends

from app.application.agent.agent_service import AgentService
from app.application.services.model_service import ModelService
from app.application.services.ingestion_service import IngestionService
from app.application.services.rag_service import RagService
from app.application.services.chat_service import ChatService
from app.application.services.web_search_service import WebSearchService
from app.config import Settings, get_settings
from app.infrastructure.ollama.ollama_client import OllamaClient
from app.infrastructure.vector_db.chroma_client import ChromaVectorClient
from app.infrastructure.web.perplexica_client import PerplexicaClient
from app.infrastructure.web.searxng_client import SearxngClient


def get_app_settings() -> Settings:
    return get_settings()


def check_http_health(url: str, timeout: float = 2.0) -> bool:
    try:
        response = httpx.get(url, timeout=timeout)
        return response.status_code < 500
    except httpx.HTTPError:
        return False


def _build_perplexica_client(settings: Settings) -> PerplexicaClient:
    return PerplexicaClient(
        settings.perplexica_url,
        timeout=settings.vane_search_timeout,
        chat_model=settings.vane_chat_model,
        embed_model=settings.vane_embed_model,
        fallback_embed_model=settings.vane_fallback_embed_model,
        optimization_mode=settings.vane_optimization_mode,
    )


def get_ollama_client(settings: Settings = Depends(get_app_settings)) -> OllamaClient:
    return OllamaClient(settings.ollama_base_url, timeout=settings.ollama_timeout)


def get_model_service(settings: Settings = Depends(get_app_settings)) -> ModelService:
    return ModelService(OllamaClient(settings.ollama_base_url, timeout=settings.ollama_timeout))


def get_chroma_client(settings: Settings = Depends(get_app_settings)) -> ChromaVectorClient:
    return ChromaVectorClient(settings.chroma_path)


def get_ingestion_service(settings: Settings = Depends(get_app_settings)) -> IngestionService:
    return IngestionService(
        settings=settings,
        llm_client=OllamaClient(settings.ollama_base_url, timeout=settings.ollama_timeout),
        vector_client=ChromaVectorClient(settings.chroma_path),
    )


def get_rag_service(settings: Settings = Depends(get_app_settings)) -> RagService:
    return RagService(
        settings=settings,
        llm_client=OllamaClient(settings.ollama_base_url, timeout=settings.ollama_timeout),
        vector_client=ChromaVectorClient(settings.chroma_path),
    )


def get_web_search_service(settings: Settings = Depends(get_app_settings)) -> WebSearchService:
    return WebSearchService(
        settings=settings,
        llm_client=OllamaClient(settings.ollama_base_url, timeout=settings.ollama_timeout),
        perplexica_client=_build_perplexica_client(settings),
        searxng_client=SearxngClient(settings.searxng_url),
    )


def get_agent_service(settings: Settings = Depends(get_app_settings)) -> AgentService:
    return AgentService(
        settings=settings,
        llm_client=OllamaClient(settings.ollama_base_url, timeout=settings.ollama_timeout),
    )


def get_chat_service(settings: Settings = Depends(get_app_settings)) -> ChatService:
    llm_client = OllamaClient(settings.ollama_base_url, timeout=settings.ollama_timeout)
    vector_client = ChromaVectorClient(settings.chroma_path)
    rag_service = RagService(settings, llm_client, vector_client)
    web_search_service = WebSearchService(
        settings=settings,
        llm_client=llm_client,
        perplexica_client=_build_perplexica_client(settings),
        searxng_client=SearxngClient(settings.searxng_url),
    )
    return ChatService(settings, llm_client, rag_service, web_search_service)
