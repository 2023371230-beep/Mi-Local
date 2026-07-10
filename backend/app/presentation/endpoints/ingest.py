from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Depends

from app.application.services.ingestion_service import IngestionService
from app.domain.schemas import IngestRequest, IngestResponse
from app.presentation.dependencies import get_ingestion_service

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
def ingest(
    request: Annotated[IngestRequest, Body()],
    service: IngestionService = Depends(get_ingestion_service),
) -> IngestResponse:
    stats = service.ingest(
        target_path=request.path,
        collection=request.collection,
        topic=request.topic,
        limit_files=request.limit_files,
    )
    return IngestResponse(
        status="success" if not stats.errors else "partial_error",
        files_processed=stats.files_processed,
        chunks_created=stats.chunks_created,
        duplicates_skipped=stats.duplicates_skipped,
        errors=stats.errors,
    )
