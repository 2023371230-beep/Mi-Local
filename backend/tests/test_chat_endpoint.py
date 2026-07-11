from __future__ import annotations

from fastapi.testclient import TestClient

from app.domain.schemas import ChatResponse
from app.presentation.dependencies import get_chat_service
from app.presentation.main import app


class FakeChatService:
    def chat(self, request):
        return ChatResponse(
            answer=f"ok:{request.mode}",
            skill_used="skill_chat_general",
            model_used="qwen2.5:7b",
            latency_ms=1,
        )


def test_chat_endpoint_returns_uniform_response():
    app.dependency_overrides[get_chat_service] = lambda: FakeChatService()
    client = TestClient(app)

    response = client.post("/chat", json={"message": "hola", "mode": "general"})

    app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == "ok:general"
    assert payload["skill_used"] == "skill_chat_general"
    assert payload["sources"] == []


def test_chat_stream_emits_ndjson_events(monkeypatch):
    """El endpoint /chat/stream emite meta -> delta -> done en NDJSON."""
    import json as _json

    from fastapi.testclient import TestClient

    from app.application.services.chat_service import ChatService
    from app.presentation.main import app
    from app.presentation.dependencies import get_chat_service

    class FakeStreamService:
        def chat_stream(self, request):
            yield {"type": "meta", "skill": "skill_chat_general", "model": "fake"}
            yield {"type": "delta", "data": "hola "}
            yield {"type": "delta", "data": "mundo"}
            yield {"type": "done", "latency_ms": 1, "rag_used": False, "web_used": False}

    app.dependency_overrides[get_chat_service] = lambda: FakeStreamService()
    try:
        client = TestClient(app)
        with client.stream("POST", "/chat/stream", json={"message": "hola"}) as response:
            assert response.status_code == 200
            events = [_json.loads(line) for line in response.iter_lines() if line]
    finally:
        app.dependency_overrides.pop(get_chat_service, None)

    types = [event["type"] for event in events]
    assert types == ["meta", "delta", "delta", "done"]
    assert "".join(e.get("data", "") for e in events if e["type"] == "delta") == "hola mundo"
