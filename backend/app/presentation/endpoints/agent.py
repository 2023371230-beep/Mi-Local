from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Query

from app.application.agent.agent_service import AgentService
from app.application.agent.safety_policy import SafetyViolation
from app.domain.schemas import (
    AgentApplyRequest,
    AgentFileResponse,
    AgentPlanRequest,
    AgentSessionRequest,
    AgentSessionResponse,
)
from app.presentation.dependencies import get_agent_service

router = APIRouter(prefix="/agent", tags=["agent"])


def _to_response(session) -> AgentSessionResponse:
    return AgentSessionResponse(**session.to_dict())


def _handle(callable_, *args, **kwargs) -> AgentSessionResponse:
    try:
        return _to_response(callable_(*args, **kwargs))
    except SafetyViolation as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from None


@router.post("/sessions", response_model=AgentSessionResponse)
def create_session(
    request: Annotated[AgentSessionRequest, Body()],
    service: AgentService = Depends(get_agent_service),
) -> AgentSessionResponse:
    return _handle(service.create_session, request.workspace_path)


@router.get("/sessions/{session_id}", response_model=AgentSessionResponse)
def get_session(session_id: str, service: AgentService = Depends(get_agent_service)) -> AgentSessionResponse:
    return _handle(service.get_session, session_id)


@router.post("/sessions/{session_id}/plan", response_model=AgentSessionResponse)
def propose_plan(
    session_id: str,
    request: Annotated[AgentPlanRequest, Body()],
    service: AgentService = Depends(get_agent_service),
) -> AgentSessionResponse:
    return _handle(service.propose_plan, session_id, request.goal)


@router.post("/sessions/{session_id}/next", response_model=AgentSessionResponse)
def propose_next_step(
    session_id: str,
    service: AgentService = Depends(get_agent_service),
) -> AgentSessionResponse:
    """Fase B: propone UN paso siguiente basado en la salida del ultimo paso (no ejecuta)."""
    return _handle(service.propose_next_step, session_id)


@router.post("/sessions/{session_id}/steps/{step_index}/propose", response_model=AgentSessionResponse)
def propose_edit(
    session_id: str,
    step_index: int,
    service: AgentService = Depends(get_agent_service),
) -> AgentSessionResponse:
    return _handle(service.propose_edit, session_id, step_index)


@router.post("/sessions/{session_id}/steps/{step_index}/apply", response_model=AgentSessionResponse)
def apply_step(
    session_id: str,
    step_index: int,
    request: Annotated[AgentApplyRequest, Body()],
    service: AgentService = Depends(get_agent_service),
) -> AgentSessionResponse:
    return _handle(service.apply_step, session_id, step_index, request.approved)


@router.post("/sessions/{session_id}/steps/{step_index}/reject", response_model=AgentSessionResponse)
def reject_step(
    session_id: str,
    step_index: int,
    service: AgentService = Depends(get_agent_service),
) -> AgentSessionResponse:
    return _handle(service.reject_step, session_id, step_index)


@router.post("/sessions/{session_id}/steps/{step_index}/revert", response_model=AgentSessionResponse)
def revert_step(
    session_id: str,
    step_index: int,
    service: AgentService = Depends(get_agent_service),
) -> AgentSessionResponse:
    return _handle(service.revert_step, session_id, step_index)


@router.get("/sessions/{session_id}/file", response_model=AgentFileResponse)
def read_file(
    session_id: str,
    path: Annotated[str, Query(min_length=1)],
    service: AgentService = Depends(get_agent_service),
) -> AgentFileResponse:
    try:
        content = service.read_file(session_id, path)
    except SafetyViolation as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from None
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from None
    return AgentFileResponse(path=path, content=content)
