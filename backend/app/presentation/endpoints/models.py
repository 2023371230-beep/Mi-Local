from __future__ import annotations

from fastapi import APIRouter, Depends

from app.application.services.model_service import ModelService
from app.domain.schemas import ModelsResponse
from app.presentation.dependencies import get_model_service

router = APIRouter(tags=["models"])


@router.get("/models", response_model=ModelsResponse)
def list_models(model_service: ModelService = Depends(get_model_service)) -> ModelsResponse:
    return ModelsResponse(models=model_service.list_models())
