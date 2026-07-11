from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_ROOT = Path(__file__).resolve().parents[1]
SETTINGS_YAML = BACKEND_ROOT / "config" / "settings.yaml"
ENV_FILE = BACKEND_ROOT / "config" / ".env"


def _load_yaml_defaults() -> dict[str, Any]:
    if not SETTINGS_YAML.exists():
        return {}
    with SETTINGS_YAML.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


class Settings(BaseSettings):
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_general_model: str = Field(default="qwen2.5:7b", alias="OLLAMA_GENERAL_MODEL")
    ollama_coder_model: str = Field(default="qwen2.5-coder:7b", alias="OLLAMA_CODER_MODEL")
    ollama_router_model: str = Field(default="llama3.2:latest", alias="OLLAMA_ROUTER_MODEL")
    ollama_embed_model: str = Field(default="qwen3-embedding:0.6b", alias="OLLAMA_EMBED_MODEL")
    ollama_timeout: float = Field(default=120.0, alias="OLLAMA_TIMEOUT")
    # Distancia maxima (L2^2 de Chroma) para aceptar un chunk como relevante (bge-m3).
    rag_max_distance: float = Field(default=1.03, alias="RAG_MAX_DISTANCE")
    rag_source_path: Path = Field(default=Path(r"C:\Users\angel\Modelo local\RAG"), alias="RAG_SOURCE_PATH")
    chroma_path: Path = Field(
        default=BACKEND_ROOT / "data" / "chroma",
        alias="CHROMA_PATH",
    )
    perplexica_url: str = Field(default="http://localhost:3000", alias="PERPLEXICA_URL")
    searxng_url: str = Field(default="http://localhost:4000", alias="SEARXNG_URL")
    vane_chat_model: str = Field(default="qwen2.5:7b", alias="VANE_CHAT_MODEL")
    vane_embed_model: str = Field(default="qwen3-embedding:0.6b", alias="VANE_EMBED_MODEL")
    vane_fallback_embed_model: str = Field(default="bge-m3", alias="VANE_FALLBACK_EMBED_MODEL")
    vane_optimization_mode: str = Field(default="speed", alias="VANE_OPTIMIZATION_MODE")
    vane_default_sources: str = Field(default="web", alias="VANE_DEFAULT_SOURCES")
    vane_search_timeout: float = Field(default=60.0, alias="VANE_SEARCH_TIMEOUT")
    web_search_fallback: str = Field(default="searxng", alias="WEB_SEARCH_FALLBACK")
    agent_workspace_base: str = Field(default=r"C:\Users\angel", alias="AGENT_WORKSPACE_BASE")
    agent_max_plan_steps: int = Field(default=8, alias="AGENT_MAX_PLAN_STEPS")
    documents_output_dir: Path = Field(default=BACKEND_ROOT / "outputs", alias="DOCUMENTS_OUTPUT_DIR")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        populate_by_name=True,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    defaults = _load_yaml_defaults()
    return Settings(**defaults)
