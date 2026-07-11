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
    service: ChatService = Depends(get_chat_se