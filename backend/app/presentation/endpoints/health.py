from __future__ import annotations

from fastapi import APIRouter, Depends

from app.config import Settings
from app.domain.schemas import HealthResponse
from app.infrastructure.vector_db.chroma_client import ChromaVectorClient
from app.infrastructure.web.perplexica_client import PerplexicaClient
from app.infrastructure.web.searxng_client import SearxngClient
from app.presentation.dependencies import check_http_health, get_app_settings

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(settings: Settings = Depends(get_app_settings)) -> HealthResponse:
    chroma_ok = ChromaVectorClient(settings.chroma_path).health()
    vane_client = PerplexicaClient(
        settings.perplexica_url,
        timeout=settings.vane_search_timeout,
        chat_model=settings.vane_chat_model,
        embed_model=settings.vane_embed_model,
        optimization_mode=settings.vane_optimization_mode,
    )
    providers_endpoint = vane_client.health()
    searxng_endpoint = SearxngClient(settings.searxng_url).health()
    vane_ok = providers_endpoint
    last_error = PerplexicaClient.last_error
    if vane_ok and not last_error:
        web_status = "ok"
    elif vane_ok or searxng_endpoint:
        web_status = "degraded"
    else:
        web_status = "error"
    ollama_ok = check_http_health(f"{settings.ollama_base_url}/api/tags")
    # ok: nucleo completo; degraded: nucleo bien pero web con problemas; error: sin ollama/chroma
    if ollama_ok and chroma_ok and web_status == "ok":
        overall = "ok"
    elif ollama_ok and chroma_ok:
        overall = "degraded"
    else:
        overall = "error"
    return HealthResponse(
        status=overall,
        ollama=ollama_ok,
        chroma=chroma_ok,
        perplexica=vane_ok,
        vane=vane_ok,
        searxng=searxng_endpoint,
        web_search={
            "status": web_status,
            "engine": "vane",
            "primary": "vane",
            "url": settings.perplexica_url,
            "providers_endpoint":