from __future__ import annotations

import time

from loguru import logger

from app.application.router.query_router import QueryRouter
from app.application.skills.skill_bases_datos import BasesDatosSkill
from app.application.skills.skill_chat_general import ChatGeneralSkill
from app.application.skills.skill_ciberseguridad import CiberseguridadSkill
from app.application.skills.skill_programacion import ProgramacionSkill
from app.application.skills.skill_rag_local import RagLocalSkill
from app.application.skills.skill_ui_ux import UiUxSkill
from app.application.skills.skill_web_search import WebSearchSkill
from app.config import Settings
from app.domain.interfaces import LLMClient
from app.domain.schemas import ChatRequest, ChatResponse
from app.application.services.rag_service import RagService
from app.application.services.web_search_service import WebSearchService


class ChatService:
    def __init__(
        self,
        settings: Settings,
        llm_client: LLMClient,
        rag_service: RagService,
        web_search_service: WebSearchService,
    ) -> None:
        self.settings = settings
        self.router = QueryRouter(settings)
        self.llm_client = llm_client
        self.rag_service = rag_service
        self.web_search_service = web_search_service

    def chat(self, request: ChatRequest) -> ChatResponse:
        started = time.perf_counter()
        decision = self.router.route(request)
        effective_request = request.model_copy(update={"collection": request.collection or decision.collection})
        model_name = request.model or decision.model_name
        skill = self._build_skill(decision.skill_name, model_name, decision.collection or "general")
        result = skill.run(effective_request)
        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info(
            "chat skill={} model={} rag={} web={} latency_ms={} reason={}",
            result.skill_used,
            result.model_used,
            result.rag_used,
            result.web_used,
            latency_ms,
            decision.reason,
        )
        return ChatResponse(
            answer=result.answer,
            skill_used=result.skill_used,
            model_used=result.model_used,
            rag_used=result.rag_used,
            web_used=result.web_used,
            web_engine=result.web_engine,
            web_fallback_used=result.web_fallback_used,
            sources=result.sources,
            latency_ms=latency_ms,
        )

    def _build_skill(self, skill_name: str, model_name: str, collection: str):
        if skill_name == "skill_programacion":
            return ProgramacionSkill(self.llm_client, model_name=model_name)
        if skill_name == "skill_ui_ux":
            return UiUxSkill(self.llm_client, model_name=model_name)
        if skill_name == "skill_ciberseguridad":
            return CiberseguridadSkill(self.llm_client, model_name=model_name)
        if skill_name == "skill_bases_datos":
            return BasesDatosSkill(self.llm_client, model_name=model_name)
        if skill_name == "skill_rag_local":
            return RagLocalSkill(self.rag_service, default_collection=collection)
        if skill_name == "skill_web_search":
            return WebSearchSkill(self.web_search_service, model_name=model_name)
        return ChatGeneralSkill(self.llm_client, model_name=model_name)
