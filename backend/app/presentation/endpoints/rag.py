from __future__ import annotations

import time
from typing import Annotated

from fastapi import APIRouter, Body, Depends

from app.application.services.rag_service import RagService
from app.domain.schemas import ChatResponse, CollectionsResponse, RagQueryRequest
from app.presentation.dependencies import get_rag_service

router = APIRouter(tags=["rag"])


@router.get("/rag/collections", response_model=CollectionsResponse)
def collections(service: RagService = Depends(get_rag_service)) -> CollectionsResponse:
    return CollectionsResponse(collections=service.list_collections())


@router.post("/rag/query", response_model=ChatResponse)
def query_rag(
    request: Annotated[RagQueryRequest, Body()],
    service: RagService = Depends(get_rag_service),
) -> ChatResponse:
    started = time.perf_counter()
    answer, sources = service.answer(request.message, request.collection, request.top_k)
    return ChatResponse(
        answer=answer,
        skill_used="skill_rag_local",
        model_used=service.settings.ollama_general_model,
        rag_used=True,
        web_used=False,
        sources=sources,
        latency_ms=int((time.perf_counter() - started) * 1000),
    )
