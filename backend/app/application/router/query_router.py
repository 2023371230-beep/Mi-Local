from __future__ import annotations

from app.config import Settings
from app.domain.models import RoutingDecision
from app.domain.schemas import ChatRequest

from .routing_rules import (
    CYBER_PATTERNS,
    DATABASE_PATTERNS,
    MODE_TO_SKILL,
    PROGRAMMING_PATTERNS,
    RAG_PATTERNS,
    SKILL_COLLECTIONS,
    UI_UX_PATTERNS,
    WEB_PATTERNS,
    matches_any,
)


class QueryRouter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def route(self, request: ChatRequest) -> RoutingDecision:
        if request.use_rag == "true":
            return self._decision_for_skill("skill_rag_local", request.collection, use_rag=True, reason="forced_rag")
        if request.use_rag == "false" and request.mode == "rag":
            return self._decision_for_skill("skill_chat_general", request.collection, reason="rag_disabled")

        if request.mode != "auto":
            skill_name = MODE_TO_SKILL[request.mode]
            return self._decision_for_skill(skill_name, request.collection, reason=f"mode={request.mode}")

        message = request.message
        if matches_any(message, RAG_PATTERNS):
            return self._decision_for_skill("skill_rag_local", request.collection, use_rag=True, reason="explicit_rag")
        if matches_any(message, WEB_PATTERNS):
            return self._decision_for_skill("skill_web_search", request.collection, use_web=True, reason="freshness_or_web")
        if matches_any(message, CYBER_PATTERNS):
            return self._decision_for_skill("skill_ciberseguridad", request.collection, reason="cyber_keywords")
        if matches_any(message, DATABASE_PATTERNS):
            return self._decision_for_skill("skill_bases_datos", request.collection, reason="database_keywords")
        if matches_any(message, UI_UX_PATTERNS):
            return self._decision_for_skill("skill_ui_ux", request.collection, reason="ui_ux_keywords")
        if matches_any(message, PROGRAMMING_PATTERNS):
            return self._decision_for_skill("skill_programacion", request.collection, reason="programming_keywords")
        return self._decision_for_skill("skill_chat_general", request.collection, reason="fallback_general")

    def _decision_for_skill(
        self,
        skill_name: str,
        collection: str | None,
        use_rag: bool = False,
        use_web: bool = False,
        reason: str = "",
    ) -> RoutingDecision:
        model = self.settings.ollama_general_model
        if skill_name in {"skill_programacion", "skill_ui_ux", "skill_bases_datos"}:
            model = self.settings.ollama_coder_model
        return RoutingDecision(
            skill_name=skill_name,
            model_name=model,
            use_rag=use_rag or skill_name == "skill_rag_local",
            use_web=use_web or skill_name == "skill_web_search",
            collection=collection or SKILL_COLLECTIONS.get(skill_name),
            reason=reason,
        )
