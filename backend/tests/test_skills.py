from __future__ import annotations

from app.application.skills.skill_programacion import ProgramacionSkill
from app.domain.schemas import ChatRequest


class FakeLLM:
    def health(self):
        return True

    def list_models(self):
        return []

    def chat(self, model, messages, options=None):
        return f"{model}: {messages[-1]['content']}"

    def embed(self, model, text):
        return [1.0]


def test_programming_skill_uses_model_and_uniform_result():
    skill = ProgramacionSkill(FakeLLM(), model_name="qwen2.5-coder:7b")

    result = skill.run(ChatRequest(message="haz un script python"))

    assert result.skill_used == "skill_programacion"
    assert result.model_used == "qwen2.5-coder:7b"
    assert "haz un script python" in result.answer
