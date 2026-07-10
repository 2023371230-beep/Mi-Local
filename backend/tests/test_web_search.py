from __future__ import annotations

from app.application.services.web_search_service import WebSearchService
from app.config import get_settings


class FakeLLM:
    def chat(self, *_, **__):
        return "answer"


class BrokenLLM:
    def chat(self, *_, **__):
        raise RuntimeError("ollama down")


class EmptyClient:
    def health(self):
        return False

    def search(self, *_, **__):
        return {"answer": "", "sources": [], "engine": "vane", "error": "offline"}


class EmptySearxngClient:
    def health(self):
        return False

    def search(self, query, limit=5):
        return []


class VaneOkClient:
    def health(self):
        return True

    def search(self, *_, **__):
        return {
            "answer": "vane answer",
            "sources": [{"source": "perplexica", "title": "T", "url": "https://e.com", "content": "c"}],
            "engine": "vane",
            "error": None,
        }


class VaneTimeoutClient:
    def health(self):
        return True

    def search(self, *_, **__):
        return {"answer": "", "sources": [], "engine": "vane", "error": "Vane search timed out after 60 seconds."}


class SearxngOkClient:
    def health(self):
        return True

    def search(self, query, limit=5):
        return [{"source": "searxng", "title": "R", "url": "https://r.com", "content": "snippet"}]


def test_web_search_returns_controlled_error_when_unavailable():
    service = WebSearchService(get_settings(), FakeLLM(), EmptyClient(), EmptySearxngClient())

    result = service.search_and_answer("latest security news")

    assert result["web_used"] is False
    assert result["answer"] == ""
    assert result["error"]


def test_web_search_uses_vane_when_available():
    service = WebSearchService(get_settings(), FakeLLM(), VaneOkClient(), SearxngOkClient())
    result = service.search_and_answer("query")
    assert result["engine"] == "vane"
    assert result["fallback_used"] is False
    assert result["vane_error"] is None
    assert result["error"] is None
    assert result["web_used"] is True


def test_web_search_falls_back_to_searxng_on_vane_timeout():
    service = WebSearchService(get_settings(), FakeLLM(), VaneTimeoutClient(), SearxngOkClient())
    result = service.search_and_answer("query")
    assert result["engine"] == "searxng"
    assert result["fallback_used"] is True
    assert "timed out" in result["vane_error"]
    assert result["error"] is None
    assert result["web_used"] is True
    assert result["answer"] == "answer"
    assert result["sources"]


def test_web_search_fallback_survives_llm_failure():
    service = WebSearchService(get_settings(), BrokenLLM(), VaneTimeoutClient(), SearxngOkClient())
    result = service.search_and_answer("query")
    assert result["engine"] == "searxng"
    assert result["web_used"] is True
    assert "snippet" in result["answer"]


def test_web_search_total_failure_is_controlled():
    service = WebSearchService(get_settings(), FakeLLM(), VaneTimeoutClient(), EmptySearxngClient())
    result = service.search_and_answer("query")
    assert result["engine"] == "none"
    assert result["web_used"] is False
    assert result["error"] == "No web engine available"
    assert result["vane_error"]
