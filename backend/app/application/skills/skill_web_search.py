from __future__ import annotations

from app.application.services.web_search_service import WebSearchService
from app.domain.models import SkillResult
from app.domain.schemas import ChatRequest


class WebSearchSkill:
    name = "skill_web_search"
    description = "Busqueda web con Perplexica y fallback controlado."

    def __init__(self, web_search_service: WebSearchService, model_name: str) -> None:
        self.web_search_service = web_search_service
        self.default_model = model_name

    def run(self, request: ChatRequest) -> SkillResult:
        result = self.web_search_service.search_and_answer(request.message, request.top_k)
        return SkillResult(
            answer=result["answer"],
            skill_used=self.name,
            model_used=self.default_model,
            rag_used=False,
            web_used=result["web_used"],
            web_engine=result.get("engine"),
            web_fallback_used=bool(result.get("fallback_used")),
            sources=result["sources"],
        )
