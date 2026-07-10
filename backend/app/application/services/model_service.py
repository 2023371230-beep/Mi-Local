from __future__ import annotations

from typing import Any

from app.domain.interfaces import LLMClient


class ModelService:
    def __init__(self, llm_client: LLMClient) -> None:
        self.llm_client = llm_client

    def list_models(self) -> list[dict[str, Any]]:
        return self.llm_client.list_models()

    def health(self) -> bool:
        return self.llm_client.health()
