from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RoutingDecision:
    skill_name: str
    model_name: str
    use_rag: bool = False
    use_web: bool = False
    collection: str | None = None
    reason: str = ""


@dataclass(frozen=True)
class SkillResult:
    answer: str
    skill_used: str
    model_used: str
    rag_used: bool = False
    web_used: bool = False
    web_engine: str | None = None
    web_fallback_used: bool = False
    sources: list[dict[str, Any]] = field(default_factory=list)
