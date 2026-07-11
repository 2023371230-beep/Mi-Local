from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from app.application.agent.agent_service import AgentService
from app.application.agent.safety_policy import SafetyPolicy, SafetyViolation
from app.config import Settings


# ------------------------------------------------------------- SafetyPolicy


def make_policy(tmp_path: Path) -> SafetyPolicy:
    return SafetyPolicy(workspace_base=tmp_path)


def test_policy_rejects_workspace_outside_base(tmp_path: Path):
    policy = make_policy(tmp_path / "base")
    (tmp_path / "base").mkdir()
    (tmp_path / "fuera").mkdir()
    with pytest.raises(SafetyViolation):
        policy.validate_workspace(str(tmp_path / "fuera"))


def test_policy_rejects_path_traversal(tmp_path: Path):
    policy = make_policy(tmp_path)
    workspace = tmp_path / "proyecto"
    workspace.mkdir()
    with pytest.raises(SafetyViolation):
        policy.resolve_inside(workspace, "../secreto.txt")


def test_policy_rejects_excluded_dirs(tmp_path: Path):
    policy = make_policy(tmp_path)
    workspace = tmp_path / "proyecto"
    (workspace / ".git").mkdir(parents=True)
    with pytest.raises(SafetyViolation):
        policy.resolve_inside(workspace, ".git/config")


def test_policy_rejects_non_editable_extension(tmp_path: Path):
    policy = make_policy(tmp_path)
    workspace = tmp_path / "proyecto"
    workspace.mkdir()
    with pytest.raises(SafetyViolation):
        policy.validate_write(workspace, "binario.exe")


def test_policy_command_whitelist(tmp_path: Path):
    policy = make_policy(tmp_path)
    assert policy.validate_command("git status") == ["git", "status"]
    assert policy.validate_command("pytest tests/test_x.py") == ["pytest", "tests/test_x.py"]
    with pytest.raises(SafetyViolation):
        policy.validate_command("rm -rf /")
    with pytest.raises(SafetyViolation):
        policy.validate_command("git push")


def test_policy_command_rejects_metacharacters(tmp_path: Path):
    policy = make_policy(tmp_path)
    for bad in ["git status && rm x", "git status | tee y", "git status; ls", "git status > out"]:
        with pytest.raises(SafetyViolation):
            policy.validate_command(bad)


# -------------------------------------------------------------- AgentService


class FakeLLM:
    def __init__(self, responses: list[str]) -> None:
        self.responses = list(responses)
        self.calls: list[dict[str, Any]] = []

    def health(self) -> bool:
        return True

    def list_models(self) -> list[dict[str, Any]]:
        return []

    def chat(self, model: str, messages: list[dict[str, str]], options: dict[str, Any] | None = None) -> str:
        self.calls.append({"model": model, "messages": messages})
        return self.responses.pop(0)

    def embed(self, model: str, text: str) -> list[float]:
        return [0.0]


def make_service(tmp_path: Path, responses: list[str]) -> tuple[AgentService, Path]:
    workspace = tmp_path / "proyecto"
    workspace.mkdir(exist_ok=True)
    settings = Settings(agent_workspace_base=str(tmp_path))
    service = AgentService(settings=settings, llm_client=FakeLLM(responses))
    return service, workspace


def test_agent_plan_parses_and_validates_steps(tmp_path: Path):
    plan = (
        '[{"kind": "edit", "path": "main.py", "description": "Crear main"},'
        ' {"kind": "command", "command": "pytest", "description": "Correr tests"},'
        ' {"kind": "command", "command": "rm -rf /", "description": "Malicioso"}]'
    )
    service, workspace = make_service(tmp_path, [plan])
    session = service.create_session(str(workspace))
    session = service.propose_plan(session.session_id, "crear main.py")

    assert len(session.steps) == 3
    assert session.steps[0].kind == "edit" and session.steps[0].status == "pending"
    assert session.steps[1].status == "pending"
    assert session.steps[2].status == "rejected"  # comando fuera de whitelist


def test_agent_edit_requires_explicit_approval(tmp_path: Path):
    plan = '[{"kind": "edit", "path": "main.py", "description": "Crear main"}]'
    proposal = '```python\nprint("hola")\n```'
    service, workspace = make_service(tmp_path, [plan, proposal])
    session = service.create_session(str(workspace))
    service.propose_plan(session.session_id, "crear main.py")
    service.propose_edit(session.session_id, 0)

    step = service.get_session(session.session_id).steps[0]
    assert step.status == "proposed"
    assert "hola" in (step.diff or "")
    assert not (workspace / "main.py").exists()  # proponer NO escribe

    with pytest.raises(SafetyViolation):
        service.apply_step(session.session_id, 0, approved=False)
    assert not (workspace / "main.py").exists()

    service.apply_step(session.session_id, 0, approved=True)
    assert (workspace / "main.py").read_text(encoding="utf-8") == 'print("hola")\n'


def test_agent_apply_without_proposal_fails(tmp_path: Path):
    plan = '[{"kind": "edit", "path": "main.py", "description": "Crear main"}]'
    service, workspace = make_service(tmp_path, [plan])
    session = service.create_session(str(workspace))
    service.propose_plan(session.session_id, "crear main.py")
    with pytest.raises(SafetyViolation):
        service.apply_step(session.session_id, 0, approved=True)


def test_agent_revert_restores_original(tmp_path: Path):
    plan = '[{"kind": "edit", "path": "main.py", "description": "Editar main"}]'
    proposal = "```python\nnuevo = True\n```"
    service, workspace = make_service(tmp_path, [plan, proposal])
    (workspace / "main.py").write_text("original = True\n", encoding="utf-8")
    session = service.create_session(str(workspace))
    service.propose_plan(session.session_id, "editar main.py")
    service.propose_edit(session.session_id, 0)
    service.apply_step(session.session_id, 0, approved=True)
    assert "nuevo" in (workspace / "main.py").read_text(encoding="utf-8")

    service.revert_step(session.session_id, 0)
    assert (workspace / "main.py").read_text(encoding="utf-8") == "original = True\n"


def test_agent_rejected_step_cannot_apply(tmp_path: Path):
    plan = '[{"kind": "command", "command": "pytest", "description": "tests"}]'
    service, workspace = make_service(tmp_path, [plan])
    session = service.create_session(str(workspace))
    service.propose_plan(session.session_id, "correr tests")
    service.reject_step(session.session_id, 0)
    with pytest.raises(SafetyViolation):
        service.apply_step(session.session_id, 0, approved=True)


def test_agent_tree_excludes_hidden_and_deps(tmp_path: Path):
    service, workspace = make_service(tmp_path, [])
    (workspace / "node_modules" / "pkg").mkdir(parents=True)
    (workspace / "node_modules" / "pkg" / "index.js").write_text("x", encoding="utf-8")
    (workspace / "src").mkdir()
    (workspace / "src" / "app.py").write_text("x", encoding="utf-8")
    session = service.create_session(str(workspace))
    assert "src/app.py" in session.tree
    assert all("node_modules" not in item for item in session.tree)


def test_agent_apply_creates_backup_and_audit_log(tmp_path: Path):
    """Cada apply deja backup fisico y linea en actions.log (.ai-local)."""
    plan = '[{"kind": "edit", "path": "main.py", "description": "Editar main"}]'
    proposal = "```python\ncambiado = True\n```"
    service, workspace = make_service(tmp_path, [plan, proposal])
    (workspace / "main.py").write_text("original = True\n", encoding="utf-8")
    session = service.create_session(str(workspace))
    service.propose_plan(session.session_id, "editar main.py")
    service.propose_edit(session.session_id, 0)
    service.apply_step(session.session_id, 0, approved=True)

    memory = workspace / ".ai-local"
    backups = list((memory / "backups").iterdir())
    assert len(backups) == 1
    assert backups[0].read_text(encoding="utf-8") == "original = True\n"

    log_lines = (memory / "actions.log").read_text(encoding="utf-8").strip().splitlines()
    actions = [__import__("json").loads(line)["action"] for line in log_lines]
    assert "plan" in actions and "apply_edit" in actions

    state = __import__("json").loads((memory / "agent_state.json").read_text(encoding="utf-8"))
    assert state["steps"][0]["status"] == "applied"


def test_agent_tree_excludes_ai_local(tmp_path: Path):
    service, workspace = make_service(tmp_path, [])
    (workspace / ".ai-local" / "backups").mkdir(parents=True)
    (workspace / ".ai-local" / "actions.log").write_text("x", encoding="utf-8")
    (workspace / "app.py").write_text("x", encoding="utf-8")
    session = service.create_session(str(workspace))
    assert "app.py" in session.tree
    assert all(".ai-local" not in item for item in session.tree)


def test_agent_next_step_proposes_correction_after_failure(tmp_path: Path):
    """Fase B: la salida de un comando fallido genera un paso de correccion pendiente."""
    plan = '[{"kind": "command", "command": "pytest", "description": "Correr tests"}]'
    next_step = '{"kind": "edit", "path": "main.py", "description": "Corregir el import roto"}'
    service, workspace = make_service(tmp_path, [plan, next_step])
    session = service.create_session(str(workspace))
    service.propose_plan(session.session_id, "arreglar tests")

    # Simular ejecucion fallida del comando (sin correr pytest real)
    step = service.get_session(session.session_id).steps[0]
    step.status = "failed"
    step.error = "ImportError: no module named foo"

    service.propose_next_step(session.session_id)
    steps = service.get_session(session.session_id).steps
    assert len(steps) == 2
    assert steps[1].kind == "edit"
    assert steps[1].status == "pending"  # requiere aprobacion, nada se ejecuto
    assert not (workspace / "main.py").exists()


def test_agent_next_step_requires_executed_step(tmp_path: Path):
    plan = '[{"kind": "command", "command": "pytest", "description": "tests"}]'
    service, workspace = make_service(tmp_path, [plan])
    session = service.create_session(str(workspace))
    service.propose_plan(session.session_id, "meta")
    with pytest.raises(ValueError):
        service.propose_next_step(session.session_id)


def test_agent_plan_includes_key_file_context(tmp_path: Path):
    """El plan lee archivos mencionados en el goal y manifiestos comunes."""
    plan = '[{"kind": "edit", "path": "app.py", "description": "x"}]'
    service, workspace = make_service(tmp_path, [plan])
    (workspace / "README.md").write_text("proyecto de prueba", encoding="utf-8")
    (workspace / "app.py").write_text("contenido_marcador_xyz", encoding="utf-8")
    session = service.create_session(str(workspace))
    service.propose_plan(session.session_id, "modifica app.py para agregar logging")

    llm = service.llm_client
    sent = llm.calls[0]["messages"][1]["content"]
    assert "contenido_marcador_xyz" in sent
    assert "proyecto de prueba" in sent
    assert "no confiables" in sent
