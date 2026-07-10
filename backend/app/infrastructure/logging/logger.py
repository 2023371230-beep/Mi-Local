from __future__ import annotations

from pathlib import Path

from loguru import logger

from app.config import BACKEND_ROOT, Settings


LOG_FILE = BACKEND_ROOT / "logs" / "backend.log"


def setup_logging(settings: Settings) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(
        LOG_FILE,
        level=settings.log_level,
        rotation="5 MB",
        retention=5,
        encoding="utf-8",
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )


def read_recent_logs(lines: int = 100) -> list[str]:
    if not LOG_FILE.exists():
        return []
    content = LOG_FILE.read_text(encoding="utf-8", errors="replace").splitlines()
    return content[-lines:]
