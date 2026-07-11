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


def test_contextual_rag_adds_sources_when_relevant():
    """Skill tematica con material relevante en su coleccion => contexto + sources."""
    from app.application.skills.skill_programacion import ProgramacionSkill
    from app.application.services.rag_service import RagService
    from app.config import get_settings
    from app.domain.schemas import ChatRequest

    class FakeLLM:
        def __init__(self):
            self.messages = None

        def health(self):
            return True

        def list_models(self):
            return []

        def chat(self, model, messages, options=None):
            self.messages = messages
            return "respuesta"

        def embed(self, model, text):
            return [0.0]

    class GoodVector:
        def query(self, collection, embedding, top_k=5, where=None):
            return [{"id": "a", "document": "usa pytest fixtures", "metadata": {"filename": "guia.md", "page": 1}, "distance": 0.5}]

    llm = FakeLLM()
    rag = RagService(get_settings(), llm, GoodVector())
    skill = ProgramacionSkill(llm, model_name="fake", rag_service=rag, rag_collection="programacion")
    result = skill.run(ChatRequest(message="como estructuro mis tests"))

    assert result.rag_used is True
    assert result.sources and result.sources[0]["filename"] == "guia.md"
    assert any("guia.md" in m["content"] for m in llm.messages if m["role"] == "system")


def test_contextual_rag_silent_when_irrelevant():
    from app.application.skills.skill_programacion import ProgramacionSkill
    from app.application.services.rag_service import RagService
    from app.config import get_settings
    from app.domain.schemas import ChatRequest

    class FakeLLM:
        def health(self):
            return True

        def list_models(self):
            return []

        def chat(self, model, messages, options=None):
            return "respuesta"

        def embed(self, model, text):
            return [0.0]

    class NoisyVector:
        def query(self, collection, embedding, top_k=5, where=None):
            return [{"id": "a", "document": "ruido", "metadata": {}, "distance": 1.4}]

    llm = FakeLLM()
    rag = RagService(get_settings(), llm, NoisyVector())
    skill = ProgramacionSkill(llm, model_name="fake", rag_service=rag, rag_collection="programacion")
    result = skill.run(ChatRequest(message="pregunta sin match"))

    assert result.rag_used is False
    assert result.sources == []
