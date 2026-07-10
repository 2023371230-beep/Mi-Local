from fastapi.testclient import TestClient

from app.presentation.main import app


def test_health_returns_uniform_status():
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert isinstance(payload["ollama"], bool)
    assert isinstance(payload["chroma"], bool)
    assert isinstance(payload["perplexica"], bool)
