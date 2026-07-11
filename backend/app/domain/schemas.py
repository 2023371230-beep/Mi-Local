from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


ChatMode = Literal[
    "auto",
    "programacion",
    "ui_ux",
    "ciberseguridad",
    "bases_datos",
    "rag",
    "web",
    "general",
]

RagMode = Literal["auto", "true", "false"]


class Source(BaseModel):
    source: str
    title: str | None = None
    content: str | None = None
    path: str | None = None
    filename: str | None = None
    page: int | None = None
    chunk_index: int | None = None
    url: str | None = None
    score: float | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    mode: ChatMode = "auto"
    use_rag: RagMode = "auto"
    collection: str | None = None
    top_k: int = Field(default=5, ge=1, le=20)
    model: str | None = None


class ChatResponse(BaseModel):
    answer: str
    skill_used: str
    model_used: str
    rag_used: bool = False
    web_used: bool = False
    web_engine: str | None = None
    web_fallback_used: bool = False
    sources: list[Source] = Field(default_factory=list)
    latency_ms: int = 0


class RagQueryRequest(BaseModel):
    message: str = Field(min_length=1)
    collection: str = "general"
    top_k: int = Field(default=5, ge=1, le=20)


class IngestRequest(BaseModel):
    path: str | None = None
    collection: str | None = None
    topic: str | None = None
    limit_files: int | None = Field(default=None, ge=1)


class IngestResponse(BaseModel):
    status: str
    files_processed: int = 0
    chunks_created: int = 0
    duplicates_skipped: int = 0
    errors: list[str] = Field(default_factory=list)


class CollectionsResponse(BaseModel):
    collections: list[str]


class WebSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
    sources: list[str] = Field(default_factory=lambda: ["web"])
    optimization_mode: str = "speed"


class WebSearchResponse(BaseModel):
    answer: str = ""
    web_used: bool
    engine: str = "vane"
    fallback_used: bool = False
    vane_error: str | None = None
    sources: list[Source] = Field(default_factory=list)
    error: str | None = None
    latency_ms: int = 0


class HealthResponse(BaseModel):
    status: str
    ollama: bool
    chroma: bool
    perplexica: bool
    vane: bool = False
    searxng: bool = False
    web_search: dict[str, object] = Field(default_factory=dict)


class ModelsResponse(BaseModel):
    