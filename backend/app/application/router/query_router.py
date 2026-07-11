from __future__ import annotations

import re

from app.config import Settings
from app.domain.interfaces import LLMClient
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
    def __init__(self, settings: Settings, router_llm: LLMClient | None = None) -> None:
        self.settings = settings
        # 2a pasada opcional: clasificador LLM ligero (llama3.2) cuando ninguna regex matchea.
        self.router_llm = router_llm

    _LLM_ROUTER_SKILLS = {
        "programacion": "skill_programacion",
        "ui_ux": "skill_ui_ux",
        "ciberseguridad": "skill_ciberseguridad",
        "bases_datos": "skill_bases_datos",
        "general": "skill_chat_general",
    }

    def _llm_classify(self, message: str) -> str | None:
        """Clasifica con el modelo router; None si falla o responde basura (fallback general)."""
        if self.router_llm is None:
            return None
        try:
            raw = self.router_llm.chat(
                self.settings.ollama_router_model,
                [
                    {
                        "role": "system",
                        "content": (
                            "Clasifica la consulta en UNA palabra exacta: programacion, ui_ux, "
                            "ciberseguridad, bases_datos o general. Responde solo esa palabra."
                        ),
                    },
                    {"role": "user", "content": message[:500]},
                ],
                options={"temperature": 0.0, "num_predict": 5},
            )
        except Exception:  # noqa: BLE001 - el router jamas debe tumbar el chat
            return None
        word = (raw or "").strip().lower().split()[0].strip(".,") if raw and raw.strip() else ""
        return self._LLM_ROUTER_SKILLS.get(word)

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
            return self._decision_for_skill(
                "skill_ciberseguridad", request.collection, reason="cyber_keywords", message=message
            )
        if matches_any(message, DATABASE_PATTERNS):
            return self._decision_for_skill(
                "skill_bases_datos", request.collection, reason="database_keywords", message=message
            )
        if matches_any(message, UI_UX_PATTERNS):
            return self._decision_for_skill(
                "skill_ui_ux", request.collection, reason="ui_ux_keywords", message=message
            )
        if matches_any(message, PROGRAMMING_PATTERNS):
            return self._decision_for_skill(
                "skill_programacion", request.collection, reason="programming_keywords", message=message
            )
        llm_skill = self._llm_classify(message)
        if llm_skill and llm_skill != "skill_chat_general":
            return self._decision_for_skill(llm_skill, request.collection, reason="llm_router", message=message)
        return self._decision_for_skill("skill_chat_general", request.collection, reason="fallback_general")

    _UI_CODE_HINT = re.compile(r"codigo|componente|\btsx\b|\bcss\b|\bhtml\b", re.IGNORECASE)

    def _decision_for_skill(
        self,
        skill_name: str,
        collection: str | None,
        use_rag: bool = False,
        use_web: bool = False,
        reason: str = "",
        message: str = "",
    ) -> RoutingDecision:
        model = self.settings.ollama_general_model
        if skill_name in {"skill_programacion", "skill_bases_datos"}:
            model = self.settings.ollama_coder_model
        elif skill_name == "skill_ui_ux" and self._UI_CODE_HINT.search(message):
            # Prosa de diseno con el modelo general; coder solo si piden codigo de UI.
            model = self.settings.ollama_coder_model
        return RoutingDecision(
            skill_name=skill_name,
            model_name=model,
            use_rag=use_rag or skill_name == "skill_rag_local",
            use_web=use_web or skill_name == "skill_web_search",
            collection=collection or SKILL_COLLECTIONS.get(skill_name),
            reason=reason,
        )
