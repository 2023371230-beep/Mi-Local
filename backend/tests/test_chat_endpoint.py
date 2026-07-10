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
