from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.responses import FileResponse

from app.application.services.document_service import (
    DOCUMENT_TEMPLATES,
    SUPPORTED_FORMATS,
    DocumentService,
)
from app.domain.schemas import (
    DocumentGenerateRequest,
    DocumentGenerateResponse,
    DocumentOutputsResponse,
)
from app.presentation.dependencies import get_document_service

router = APIRouter(prefix="/documents", tags=["documents"])

_MEDIA_TYPES = {
    "md": "text/markdown",
    "html": "text/html",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "pdf": "application/pdf",
}


@router.post("/generate", response_model=DocumentGenerateResponse)
def generate(
    request: Annotated[DocumentGenerateRequest, Body()],
    service: DocumentService = Depends(get_document_service),
) -> DocumentGenerateResponse:
    try:
        result = service.generate(
            doc_type=request.doc_type,
            title=request.title,
            instructions=request.instructions,
            output_format=request.output_format,
            use_rag=request.use_rag,
            collection=request.collection,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None
    return DocumentGenerateResponse(**result)


@router.get("/outputs", response_model=DocumentOutputsResponse)
def outputs(service: DocumentService = Depends(get_document_service)) -> DocumentOutputsResponse:
    return DocumentOutputsResponse(
        outputs=service.list_outputs(),
        doc_types=sorted(DOCUMENT_TEMPLATES),
        formats=list(SUPPORTED_FORMATS),
    )


@router.get("/download/{filename}")
def download(filename: str, service: DocumentService = Depends(get_document_service)) -> FileResponse:
    try:
        path = service.resolve_output(filename)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"No existe: {filename}") from None
    suffix = path.suffix.lstrip(".").lower()
    return FileResponse(
        path,
        media_type=_MEDIA_TYPES.get(suffix, "application/octet-stream"),
        filename=path.name,
    )
