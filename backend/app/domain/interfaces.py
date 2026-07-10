from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.domain.models import SkillResult
from app.domain.schemas import ChatRequest


class LLMClient(ABC):
    @abstractmethod
    def health(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_models(self) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def chat(self, model: str, messages: list[dict[str, str]], options: dict[str, Any] | None = None) -> str:
        raise NotImplementedError

    @abstractmethod
    def embed(self, model: str, text: str) -> list[float]:
        raise NotImplementedError


class VectorDB(ABC):
    @abstractmethod
    def health(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_collections(self) -> list[str]:
        raise NotImplementedError


class SearchEngine(ABC):
    @abstractmethod
    def health(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def search(self, query: str, limit: int = 5) -> list[dict[str, Any]]:
        raise NotImplementedError


class BaseSkillProtocol(ABC):
    name: str
    description: str
    default_model: str

    @abstractmethod
    def run(self, request: ChatRequest) -> SkillResult:
        raise NotImplementedError
