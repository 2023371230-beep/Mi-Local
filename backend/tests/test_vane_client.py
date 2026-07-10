from __future__ import annotations

import httpx

from app.infrastructure.web.perplexica_client import PerplexicaClient


def test_vane_provider_and_model_selection():
    client = PerplexicaClient("http://localhost:3000")
    providers = [
        {"id": "t1", "name": "Transformers", "chatModels": [], "embeddingModels": []},
        {
            "id": "o1",
            "name": "http://host.docker.internal:11434",
            "chatModels": [{"name": "qwen2.5:7b", "key": "qwen2.5:7b"}],
            "embeddingModels": [{"name": "qwen3-embedding:0.6b", "key": "qwen3-embedding:0.6b"}],
        },
    ]

    provider = client.find_ollama_provider(providers)

    assert provider is not None
    assert provider["id"] == "o1"
    assert client.find_chat_model(provider) == "qwen2.5:7b"
    assert client.find_embedding_model(provider) == "qwen3-embedding:0.6b"


def test_vane_provider_detected_by_model_tag_shape():
    """Provider con nombre generico pero modelos con forma de tag Ollama."""
    client = PerplexicaClient("http://localhost:3000")
    providers = [
        {"id": "x1", "name": "Custom Local", "chatModels": [{"key": "qwen2.5:7b"}], "embeddingModels": []},
    ]
    provider = client.find_ollama_provider(providers)
    assert provider is not None
    assert provider["id"] == "x1"


def test_vane_provider_detected_by_configured_chat_model():
    client = PerplexicaClient("http://localhost:3000", chat_model="mi modelo custom")
    providers = [
        {"id": "a", "name": "OpenAI", "chatModels": [{"key": "gpt-4o"}], "embeddingModels": []},
        {"id": "b", "name": "Local", "chatModels": [{"key": "mi modelo custom"}], "embeddingModels": []},
    ]
    provider = client.find_ollama_provider(providers)
    assert provider is not None
    assert provider["id"] == "b"


def test_vane_embedding_fallback_to_bge_m3():
    client = PerplexicaClient("http://localhost:3000", fallback_embed_model="bge-m3")
    provider = {"embeddingModels": [{"key": "bge-m3:latest"}]}
    assert client.find_embedding_model(provider) == "bge-m3:latest"


def test_vane_providers_cache(monkeypatch):
    calls = {"count": 0}

    class FakeResponse:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return {"providers": [{"id": "o1", "name": "ollama", "chatModels": [], "embeddingModels": []}]}

    def fake_get(*_, **__):
        calls["count"] += 1
        return FakeResponse()

    monkeypatch.setattr(httpx, "get", fake_get)
    client = PerplexicaClient("http://localhost:3000")
    client.get_providers()
    client.get_providers()
    assert calls["count"] == 1
    client.get_providers(use_cache=False)
    assert calls["count"] == 2


def test_vane_search_normalizes_sources(monkeypatch):
    class FakeGetResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "providers": [
                    {
                        "id": "o1",
                        "name": "http://host.docker.internal:11434",
                        "chatModels": [{"key": "qwen2.5:7b"}],
                        "embeddingModels": [{"key": "qwen3-embedding:0.6b"}],
                    }
                ]
            }

    class FakeStreamResponse:
        def raise_for_status(self):
            return None

        def iter_lines(self):
            yield '{"type":"init","data":"Stream connected"}'
            yield (
                '{"type":"sources","data":[{"content":"snippet",'
                '"metadata":{"title":"Title","url":"https://example.com"}}]}'
            )
            yield '{"type":"response","data":"ans"}'
            yield '{"type":"response","data":"wer"}'
            yield '{"type":"done"}'

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    monkeypatch.setattr(httpx, "get", lambda *_, **__: FakeGetResponse())
    monkeypatch.setattr(httpx, "stream", lambda *_, **__: FakeStreamResponse())

    result = PerplexicaClient("http://localhost:3000").search("query")

    assert result["answer"] == "answer"
    assert result["sources"][0]["title"] == "Title"
    assert result["sources"][0]["url"] == "https://example.com"
    assert result["error"] is None


def test_vane_search_returns_error_on_timeout(monkeypatch):
    class FakeGetResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "providers": [
                    {
                        "id": "o1",
                        "name": "http://host.docker.internal:11434",
                        "chatModels": [{"key": "qwen2.5:7b"}],
                        "embeddingModels": [{"key": "qwen3-embedding:0.6b"}],
                    }
                ]
            }

    monkeypatch.setattr(httpx, "get", lambda *_, **__: FakeGetResponse())
    monkeypatch.setattr(httpx, "stream", lambda *_, **__: (_ for _ in ()).throw(httpx.TimeoutException("timeout")))

    result = PerplexicaClient("http://localhost:3000", timeout=1).search("query")

    assert result["answer"] == ""
    assert "timed out" in result["error"]
