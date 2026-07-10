from __future__ import annotations

import os

import pytest

from app.config import get_settings
from app.infrastructure.web.perplexica_client import PerplexicaClient


@pytest.mark.skipif(os.getenv("RUN_INTEGRATION_TESTS") != "true", reason="Integration tests disabled")
def test_vane_providers_real():
    settings = get_settings()
    client = PerplexicaClient(settings.perplexica_url, timeout=10)

    providers = client.get_providers()

    assert providers
    assert client.find_ollama_provider(providers) is not None
