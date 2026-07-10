from __future__ import annotations

from fastapi import APIRouter, Query

from app.infrastructure.logging.logger import read_recent_logs

router = APIRouter(tags=["logs"])


@router.get("/logs")
def logs(lines: int = Query(default=100, ge=1, le=500)) -> dict:
    return {"logs": read_recent_logs(lines)}
