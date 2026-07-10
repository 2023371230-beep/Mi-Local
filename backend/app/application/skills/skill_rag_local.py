from __future__ import annotations

from app.application.services.rag_service import RagService
from app.domain.models import SkillResult
from app.domain.schemas import ChatRequest


class RagLocalSkill:
    name = "skill_rag_local"
    description = "Respuestas basadas en ChromaDB local con fuentes."

    def __init__(self, rag_service: RagService, default_collection: str = "general") -> None:
        self.rag_service = rag_service
        self.default_collection = default_collection
        self.default_model = rag_service.settings.ollama_general_model

    def run(self, request: ChatRequest) -> SkillResult:
        collection = request.collection or self.default_collection
        answer, sources = self.rag_service.answer(request.message, collection, request.top_k)
        return SkillResult(
            answer=answer,
            skill_used=self.name,
            model_used=self.default_model,
            rag_used=True,
            web_used=False,
            sources=sources,
        )
