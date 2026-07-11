from __future__ import annotations

import json
from typing import Annotated

from fastapi import APIRouter, Body, Depends
from fastapi.responses import StreamingResponse

from app.application.services.chat_service import ChatService
from app.domain.schemas import ChatRequest, ChatResponse
from app.presentation.dependencies import get_chat_service

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    request: Annotated[ChatRequest, Body()],
    service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    return service.chat(request)


@router.post("/chat/stream")
def chat_stream(
    request: Annotated[ChatRequest, Body()],
    service: ChatService = Depends(get_chat_service),
) -> StreamingResponse:
    """Chat en streaming NDJSON: meta -> delta* -> (sources) -> done | error."""

    def event_stream():
        try:
            for event in service.chat_stream(request):
                yield json.dumps(event, ensure_ascii=False) + "\n"
        except Exception as exc:  # noqa: BLE001 - el stream debe cerrar limpio
            yield json.dumps({"type": "error", "data": str(exc)}, ensure_ascii=False) + "\n"

    return StreamingResponse(event_stream(), media_type="application/x-ndjson")
