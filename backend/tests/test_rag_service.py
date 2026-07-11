from __future__ import annotations

from app.infrastructure.parsers.text_splitter import TextSplitter


def test_text_splitter_creates_overlap_chunks():
    text = " ".join(f"palabra{i}" for i in range(80))
    splitter = TextSplitter(chunk_size=120, overlap=20)

    chunks = splitter.split(text)

    assert len(chunks) > 1
    assert all(len(chunk) <= 120 for chunk in chunks)


def test_text_splitter_rejects_invalid_overlap():
    try:
        TextSplitter(chunk_size=100, overlap=100)
    except ValueError as exc:
        assert "overlap" in str(exc)
    else:
        raise AssertionError("Expected ValueError")


def test_rag_answer_rejects_low_relevance(monkeypatch):
    """Chunks con distancia > umbral no llegan al modelo (anti-alucinacion)."""
    from app.application.services.rag_service import RagService
    from app.config import get_settings

    class FakeLLM:
        def health(self):
            return True

        def list_models(self):
            return []

        def chat(self, model, messages, options=None):
            raise AssertionError("El modelo NO debe llamarse si nada es relevante")

        def embed(self, model, text):
            return [0.0]

    class FakeVector:
        def query(self, collection, embedding, top_k=5, where=None):
            return [
                {"id": "x", "document": "ruido", "metadata": {}, "distance": 1.12},
                {"id": "y", "document": "mas ruido", "metadata": {}, "distance": 1.25},
            ]

    service = RagService(get_settings(), FakeLLM(), FakeVector())
    answer, sources = service.answer("pregunta sin match", "ui_ux", 5)
    assert sources == []
    assert "suficientemente relevante" in answer
