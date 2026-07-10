from __future__ import annotations

import httpx

from app.infrastructure.ollama.ollama_client import OllamaClient


def test_ollama_health_false_when_unavailable(monkeypatch):
    def fake_get(*_, **__):
        raise httpx.ConnectError("offline")

    monkeypatch.setattr(httpx, "get", fake_get)
    client = OllamaClient("http://localhost:11434")

    assert client.health() is False


def test_ollama_list_models_parses_response(monkeypatch):
    class FakeResponse:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return {"models": [{"name": "qwen2.5:7b"}]}

    monkeypatch.setattr(httpx, "get", lambda *_, **__: FakeResponse())
    client = OllamaClient("http://localhost:11434")

    assert client.list_models() == [{"name": "qwen2.5:7b"}]


def test_ollama_chat_parses_message(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"message": {"content": "ok"}}

    monkeypatch.setattr(httpx, "post", lambda *_, **__: FakeResponse())
    client = OllamaClient("http://localhost:11434")

    assert client.chat("qwen2.5:7b", [{"role": "user", "content": "hola"}]) == "ok"


def test_ollama_embed_parses_embeddings(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"embeddings": [[0.1, 0.2, 0.3]]}

    monkeypatch.setattr(httpx, "post", lambda *_, **__: FakeResponse())
    client = OllamaClient("http://localhost:11434")

    assert client.embed("qwen3-embedding:0.6b", "redes") == [0.1, 0.2, 0.3]
