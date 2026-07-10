from fastapi.testclient import TestClient

from app.presentation.main import app


def test_logs_endpoint_returns_list():
    client = TestClient(app)

    response = client.get("/logs")

    assert response.status_code == 200
    assert isinstance(response.json()["logs"], list)
