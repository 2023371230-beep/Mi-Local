from fastapi.testclient import TestClient

from app.presentation.main import app


def test_health_returns_coherent_status():
    """El status global se deriva de los checks reales (ok/degraded/error).

    No se asegura "ok" literal: este test corre contra los servicios reales de la
    maquina y el estado de Vane/SearXNG es variable. Lo que si es contrato:
    - status es uno de los tres valores validos
    - si ollama o chroma caen, el status NO puede ser "ok"
    - los flags de componentes son booleanos
    """
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] in ("ok", "degraded", "error")
    assert isinstance(payload["ollama"], bool)
    assert isinstance(payload["chroma"], bool)
    assert isinstance(payload["perplexica"], bool)
    if not (payload["ollama"] and payload["chroma"]):
        assert payload["status"] == "error"
    elif payload["status"] == "ok":
        assert payload["web_search"]["status"] == "ok"
