from __future__ import annotations

import time
from typing import Annotated

from fastapi import APIRouter, Body, Depends

from app.application.services.web_search_service import WebSearchService
from app.domain.schemas import WebSearchRequest, WebSearchResponse
from app.presentation.dependencies import get_web_search_service

router = APIRouter(tags=["web"])


@router.post("/web/search", response_model=WebSearchResponse)
def web_search(
    request: Annotated[WebSearchRequest, Body()],
    service: WebSearchService = Depends(get_web_search_service),
) -> WebSearchResponse:
    started = time.perf_counter()
    result = service.search_and_answer(
        request.query,
        request.top_k,
        sources=request.sources,
        optimization_mode=request.optimization_mode,
    )
    return WebSearchResponse(
        answer=result["answer"],
        web_used=result["web_used"],
        engine=result["engine"],
        fallback_used=bool(result.get("fallback_used")),
        vane_error=result.get("vane_error"),
        sources=result["sources"],
        error=result["error"],
        latency_ms=int((time.perf_counter() - started) * 1000),
    )
