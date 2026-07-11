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
        "\nSi la peticion es ambigua en un punto que cambia la respuesta (version, stack, objetivo), "
        "haz UNA sola pregunta de aclaracion antes de responder; si puedes asumir lo mas comun, "
        "asumelo y dilo explicitamente."
    )

    def build_messages(self, request: ChatRequest) -> list[dict[str, str]]:
        system = self.system_prompt + self._CLARIFY_RULE
        messages: list[dict[str, str]] = [{"role": "system", "content": system}]
        for question, answer in self.few_shot:
            messages.append({"role": "user", "content": question})
            messages.append({"role": "assistant", "content": answer})
        messages.append({"role": "user", "content": request.message})
        return messages

    def run(self, request: ChatRequest) -> SkillResult:
        options: dict[str, float | int] = {"temperature": 0.2, "num_ctx": 4096}
        options.update(self.chat_options)
        answer = self.llm_client.chat(
            self.default_model,
            self.build_messages(request),
            options=options,
        )
        return SkillResult(answer=answer, skill_used=self.name, model_used=self.default_model)
