from __future__ import annotations

from app.domain.interfaces import LLMClient
from app.domain.models import SkillResult
from app.domain.schemas import ChatRequest


class BaseSkill:
    name = "base_skill"
    description = "Base skill"
    default_model = ""
    system_prompt = "Eres un asistente tecnico."
    # Ejemplos few-shot opcionales: pares (pregunta, respuesta ideal). En modelos
    # locales chicos ensenan el formato esperado mejor que cualquier instruccion.
    few_shot: tuple[tuple[str, str], ...] = ()
    # Opciones de generacion por skill (se mezclan sobre los defaults).
    chat_options: dict[str, float | int] = {}

    def __init__(self, llm_client: LLMClient, model_name: str | None = None) -> None:
        self.llm_client = llm_client
        self.default_model = model_name or self.default_model

    # Regla comun a todas las skills: no adivinar cuando falta un dato critico.
    _CLARIFY_RULE = (
        "\nSi la p