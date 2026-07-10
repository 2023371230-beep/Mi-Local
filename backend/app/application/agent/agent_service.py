from __future__ import annotations

import difflib
import json
import re
import subprocess
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger

from app.application.agent.safety_policy import SafetyPolicy, SafetyViolation
from app.config import Settings
from app.domain.interfaces import LLMClient

_JSON_ARRAY_PATTERN = re.compile(r"\[.*\]", re.DOTALL)
_CODE_FENCE_PATTERN = re.compile(r"```[a-zA-Z0-9]*\n(.*?)```", re.DOTALL)

_PLAN_SYSTEM_PROMPT = """Eres un agente de programacion que SOLO planifica. Responde UNICAMENTE con un array JSON.
Cada paso es un objeto con:
- "kind": "edit" (modificar/crear un archivo) o "command" (ejecutar un comando de la whitelist)
- "path": ruta relativa del archivo (solo para kind=edit)
- "command": comando exacto (solo para kind=command); permitidos: {allowed}
- "description": que hace el paso y por que, en espanol, 1-2 frases

Reglas: maximo {max_steps} pasos, rutas relativas al workspace, no inventes archivos que no esten
en el arbol salvo que el objetivo pida crearlos. Sin texto fuera del JSON."""

_EDIT_SYSTEM_PROMPT = """Eres un asistente de programacion. Recibes el contenido actual de un archivo
(o vacio si es nuevo) y una instruccion. Devuelve UNICAMENTE el contenido COMPLETO y final del archivo
dentro de un unico bloque ```...```. Sin explicaciones fuera del bloque. Conserva todo lo que no deba cambiar."""


@dataclass
class AgentStep:
    kind: str  # "edit" | "command"
    description: str
    path: str | None = None
    command: str | None = None
    status: str = "pending"  # pending | proposed | applied | executed | rejected | failed
    diff: str | None = None
    proposed_content: str | None = None
    original_content: str | None = None
    output: str | None = None
    error: str | None = None

    def to_dict(self, index: int) -> dict[str, Any]:
        return {
            "index": index,
            "kind": self.kind,
            "description": self.description,
            "path": self.path,
            "command": self.command,
            "status": self.status,
            "diff": self.diff,
            "output": self.output,
            "error": self.error,
        }


@dataclass
class AgentSession:
    session_id: str
    workspace: Path
    tree: list[str]
    goal: str | None = None
    steps: list[AgentStep] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    events: list[str] = field(default_factory=list)

    def log_event(self, message: str) -> None:
        stamp = datetime.now(timezone.utc).strftime("%H:%M:%S")
        self.events.append(f"[{stamp}] {message}")
        logger.info("agent[{}]: {}", self.session_id[:8], message)

    def to_dict(self) -> dict[str, Any]:
        return {
            "session_id": self.session_id,
            "workspace": str(self.workspace),
            "tree": self.tree,
            "goal": self.goal,
            "steps": [step.to_dict(i) for i, step in enumerate(self.steps)],
            "created_at": self.created_at,
            "events": self.events[-50:],
        }


class AgentService:
    """Modo agente con aprobacion obligatoria.

    Flujo: create_session -> propose_plan -> (por paso) propose_edit -> apply_step(approved=True).
    Ninguna escritura ni comando se ejecuta sin `approved=True` explicito del usuario;
    no existe modo full-auto por decision de diseno.
    """

    _sessions: dict[str, AgentSession] = {}
    _lock = threading.Lock()

    def __init__(self, settings: Settings, llm_client: LLMClient, policy: SafetyPolicy | None = None) -> None:
        self.settings = settings
        self.llm_client = llm_client
        self.policy = policy or SafetyPolicy(workspace_base=Path(settings.agent_workspace_base))
        self.max_steps = settings.agent_max_plan_steps

    # ------------------------------------------------------------- sesiones

    def create_session(self, workspace_path: str) -> AgentSession:
        workspace = self.policy.validate_workspace(workspace_path)
        session = AgentSession(
            session_id=uuid.uuid4().hex,
            workspace=workspace,
            tree=self.policy.iter_tree(workspace),
        )
        with self._lock:
            self._sessions[session.session_id] = session
        session.log_event(f"Sesion creada sobre {workspace} ({len(session.tree)} archivos)")
        return session

    def get_session(self, session_id: str) -> AgentSession:
        with self._lock:
            session = self._sessions.get(session_id)
        if session is None:
            raise KeyError(f"Sesion no encontrada: {session_id}")
        return session

    def read_file(self, session_id: str, relative: str) -> str:
        session = self.get_session(session_id)
        path = self.policy.validate_read(session.workspace, relative)
        return path.read_text(encoding="utf-8", errors="replace")

    # ------------------------------------------------------------------ plan

    def propose_plan(self, session_id: str, goal: str) -> AgentSession:
        session = self.get_session(session_id)
        session.goal = goal
        tree_text = "\n".join(session.tree[:200])
        prompt = _PLAN_SYSTEM_PROMPT.format(
            allowed=", ".join(self.policy.allowed_commands),
            max_steps=self.max_steps,
        )
        raw = self.llm_client.chat(
            self.settings.ollama_coder_model,
            [
                {"role": "system", "content": prompt},
                {"role": "user", "content": f"Objetivo: {goal}\n\nArbol del workspace:\n{tree_text}"},
            ],
            options={"temperature": 0.1, "num_ctx": 4096},
        )
        steps = self._parse_plan(raw)
        session.steps = steps
        session.log_event(f"Plan propuesto con {len(steps)} pasos (pendiente de aprobacion)")
        return session

    def _parse_plan(self, raw: str) -> list[AgentStep]:
        match = _JSON_ARRAY_PATTERN.search(raw or "")
        if not match:
            raise ValueError("El modelo no devolvio un plan JSON valido.")
        try:
            items = json.loads(match.group(0))
        except ValueError as exc:
            raise ValueError(f"Plan JSON invalido: {exc}") from None
        steps: list[AgentStep] = []
        for item in items[: self.max_steps]:
            if not isinstance(item, dict):
                continue
            kind = str(item.get("kind", "")).strip().lower()
            description = str(item.get("description", "")).strip() or "(sin descripcion)"
            if kind == "edit" and item.get("path"):
                steps.append(AgentStep(kind="edit", description=description, path=str(item["path"]).strip()))
            elif kind == "command" and item.get("command"):
                step = AgentStep(kind="command", description=description, command=str(item["command"]).strip())
                try:
                    self.policy.validate_command(step.command)
                except SafetyViolation as exc:
                    step.status = "rejected"
                    step.error = f"Rechazado por politica: {exc}"
                steps.append(step)
        if not steps:
            raise ValueError("El plan no contiene pasos validos.")
        return steps

    # ----------------------------------------------------------------- edits

    def propose_edit(self, session_id: str, step_index: int) -> AgentSession:
        session = self.get_session(session_id)
        step = self._get_step(session, step_index)
        if step.kind != "edit":
            raise ValueError("Solo los pasos 'edit' generan propuestas de diff.")
        if step.status == "rejected":
            raise ValueError("El paso fue rechazado.")
        target = self.policy.validate_write(session.workspace, step.path or "")
        current = ""
        if target.exists():
            current = self.policy.validate_read(session.workspace, step.path or "").read_text(
                encoding="utf-8", errors="replace"
            )
        raw = self.llm_client.chat(
            self.settings.ollama_coder_model,
            [
                {"role": "system", "content": _EDIT_SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Objetivo general: {session.goal}\n"
                        f"Instruccion del paso: {step.description}\n"
                        f"Archivo: {step.path}\n\n"
                        f"Contenido actual:\n```\n{current}\n```"
                    ),
                },
            ],
            options={"temperature": 0.1, "num_ctx": 8192},
        )
        proposed = self._extract_content(raw)
        step.original_content = current
        step.proposed_content = proposed
        step.diff = "".join(
            difflib.unified_diff(
                current.splitlines(keepends=True),
                proposed.splitlines(keepends=True),
                fromfile=f"a/{step.path}",
                tofile=f"b/{step.path}",
            )
        )
        step.status = "proposed"
        step.error = None
        session.log_event(f"Diff propuesto para {step.path} (pendiente de aprobacion)")
        return session

    def _extract_content(self, raw: str) -> str:
        match = _CODE_FENCE_PATTERN.search(raw or "")
        if match:
            return match.group(1)
        cleaned = (raw or "").strip()
        if not cleaned:
            raise ValueError("El modelo devolvio contenido vacio.")
        return cleaned + ("\n" if not cleaned.endswith("\n") else "")

    # ----------------------------------------------------------------- apply

    def apply_step(self, session_id: str, step_index: int, approved: bool) -> AgentSession:
        """Unica via de escritura/ejecucion. Exige approved=True explicito."""
        if approved is not True:
            raise SafetyViolation("El paso requiere aprobacion explicita (approved=true).")
        session = self.get_session(session_id)
        step = self._get_step(session, step_index)
        if step.status == "rejected":
            raise SafetyViolation("No se puede aplicar un paso rechazado.")
        if step.kind == "edit":
            if step.status != "proposed" or step.proposed_content is None:
                raise SafetyViolation("El paso no tiene un diff propuesto que aprobar.")
            target = self.policy.validate_write(session.workspace, step.path or "")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(step.proposed_content, encoding="utf-8")
            step.status = "applied"
            session.log_event(f"Cambio aplicado en {step.path} con aprobacion del usuario")
        elif step.kind == "command":
            self._run_command(session, step)
        else:
            raise ValueError(f"Tipo de paso desconocido: {step.kind}")
        return session

    def reject_step(self, session_id: str, step_index: int) -> AgentSession:
        session = self.get_session(session_id)
        step = self._get_step(session, step_index)
        step.status = "rejected"
        session.log_event(f"Paso {step_index} rechazado por el usuario")
        return session

    def revert_step(self, session_id: str, step_index: int) -> AgentSession:
        """Restaura el contenido original de un paso 'edit' ya aplicado."""
        session = self.get_session(session_id)
        step = self._get_step(session, step_index)
        if step.kind != "edit" or step.status != "applied" or step.original_content is None:
            raise SafetyViolation("Solo se puede revertir un edit aplicado.")
        target = self.policy.validate_write(session.workspace, step.path or "")
        target.write_text(step.original_content, encoding="utf-8")
        step.status = "proposed"
        session.log_event(f"Cambio revertido en {step.path}")
        return session

    # -------------------------------------------------------------- comandos

    def _run_command(self, session: AgentSession, step: AgentStep) -> None:
        tokens = self.policy.validate_command(step.command or "")
        session.log_event(f"Ejecutando comando aprobado: {' '.join(tokens)}")
        try:
            result = subprocess.run(
                tokens,
                cwd=session.workspace,
                capture_output=True,
                text=True,
                timeout=self.policy.command_timeout,
                shell=False,
            )
            output = (result.stdout or "") + (("\n" + result.stderr) if result.stderr else "")
            step.output = output[-8000:]
            if result.returncode == 0:
                step.status = "executed"
                step.error = None
            else:
                step.status = "failed"
                step.error = f"Exit code {result.returncode}"
        except FileNotFoundError:
            step.status = "failed"
            step.error = f"Ejecutable no encontrado: {tokens[0]}"
        except subprocess.TimeoutExpired:
            step.status = "failed"
            step.error = f"Timeout tras {self.policy.command_timeout}s"

    # ----------------------------------------------------------------- utils

    def _get_step(self, session: AgentSession, index: int) -> AgentStep:
        if index < 0 or index >= len(session.steps):
            raise KeyError(f"Paso fuera de rango: {index}")
        return session.steps[index]
