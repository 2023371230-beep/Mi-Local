from __future__ import annotations

import re
import shlex
from dataclasses import dataclass, field
from pathlib import Path


class SafetyViolation(Exception):
    """Operacion bloqueada por la politica de seguridad del agente."""


# Metacaracteres que permitirian encadenar o redirigir comandos.
_SHELL_METACHARACTERS = ("&", "|", ";", ">", "<", "`", "$", "(", ")", "\n", "\r")

# Directorios que el agente nunca lista ni toca.
_EXCLUDED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".next", "dist", "build", ".pytest_cache", "chroma", ".ai-local"}

# Archivos con secretos: el agente no puede leerlos NI escribirlos, aunque le den la ruta exacta.
_SECRET_PATTERNS = (
    re.compile(r"^\.env(?!\.example$)(\..+)?$", re.IGNORECASE),
    re.compile(r".*\.(pem|key|pfx|p12|crt|der)$", re.IGNORECASE),
    re.compile(r"^id_(rsa|dsa|ecdsa|ed25519)(\.pub)?$", re.IGNORECASE),
    re.compile(r"^(credentials|secrets?)(\..+)?$", re.IGNORECASE),
    re.compile(r".*secret.*\.(json|yaml|yml|toml)$", re.IGNORECASE),
)

# Extensiones consideradas texto editable. Todo lo demas es solo lectura-denegada.
_EDITABLE_SUFFIXES = {
    ".py", ".ts", ".tsx", ".js", ".jsx", ".json", ".md", ".txt", ".yaml", ".yml",
    ".toml", ".ini", ".cfg", ".css", ".html", ".sql", ".ps1", ".sh", ".env.example",
}


@dataclass(frozen=True)
class SafetyPolicy:
    """Reglas duras del modo agente. Nada se ejecuta ni escribe fuera de ellas.

    - El workspace debe vivir bajo `workspace_base`.
    - Lecturas y escrituras solo dentro del workspace y en archivos de texto.
    - Comandos: solo los de la whitelist (por prefijo exacto de tokens),
      sin metacaracteres de shell, ejecutados sin shell.
    - Ninguna accion de escritura/ejecucion ocurre sin aprobacion explicita;
      eso lo garantiza el servicio, esta clase valida los limites fisicos.
    """

    workspace_base: Path
    max_file_bytes: int = 200_000
    max_tree_files: int = 500
    command_timeout: float = 120.0
    allowed_commands: tuple[str, ...] = (
        "git status",
        "git diff",
        "git log",
        "python -m pytest",
        "pytest",
        "python -m py_compile",
        "npm run lint",
        "npm run build",
        "npm test",
        "pip list",
    )
    excluded_dirs: frozenset[str] = field(default_factory=lambda: frozenset(_EXCLUDED_DIRS))

    # ------------------------------------------------------------- workspace

    def validate_workspace(self, raw_path: str) -> Path:
        workspace = Path(raw_path).resolve()
        base = self.workspace_base.resolve()
        if not workspace.exists() or not workspace.is_dir():
            raise SafetyViolation(f"El workspace no existe o no es un directorio: {workspace}")
        if workspace != base and base not in workspace.parents:
            raise SafetyViolation(f"El workspace debe estar dentro de {base}")
        return workspace

    def resolve_inside(self, workspace: Path, relative: str) -> Path:
        """Resuelve una ruta relativa garantizando que quede dentro del workspace."""
        if not relative or relative.strip() == "":
            raise SafetyViolation("Ruta vacia")
        candidate = (workspace / relative).resolve()
        if candidate != workspace and workspace not in candidate.parents:
            raise SafetyViolation(f"Ruta fuera del workspace: {relative}")
        for part in candidate.relative_to(workspace).parts:
            if part in self.excluded_dirs:
                raise SafetyViolation(f"Directorio excluido por politica: {part}")
        if any(pattern.match(candidate.name) for pattern in _SECRET_PATTERNS):
            raise SafetyViolation(f"Archivo de secretos bloqueado por politica: {candidate.name}")
        return candidate

    def validate_read(self, workspace: Path, relative: str) -> Path:
        path = self.resolve_inside(workspace, relative)
        if not path.exists() or not path.is_file():
            raise SafetyViolation(f"El archivo no existe: {relative}")
        if path.stat().st_size > self.max_file_bytes:
            raise SafetyViolation(f"Archivo demasiado grande (> {self.max_file_bytes} bytes): {relative}")
        return path

    def validate_write(self, workspace: Path, relative: str) -> Path:
        path = self.resolve_inside(workspace, relative)
        suffix = path.suffix.lower()
        if suffix not in _EDITABLE_SUFFIXES:
            raise SafetyViolation(f"Extension no editable por politica: {suffix or '(sin extension)'}")
        if path.exists() and path.stat().st_size > self.max_file_bytes:
            raise SafetyViolation(f"Archivo demasiado grande para editar: {relative}")
        return path

    # -------------------------------------------------------------- comandos

    def validate_command(self, raw_command: str) -> list[str]:
        """Devuelve el comando tokenizado si esta permitido; lanza si no."""
        command = (raw_command or "").strip()
        if not command:
            raise SafetyViolation("Comando vacio")
        for char in _SHELL_METACHARACTERS:
            if char in command:
                raise SafetyViolation(f"Metacaracter de shell no permitido: {char!r}")
        try:
            tokens = shlex.split(command, posix=True)
        except ValueError as exc:
            raise SafetyViolation(f"Comando invalido: {exc}") from None
        if any(".." in token for token in tokens):
            raise SafetyViolation("'..' no permitido en argumentos")
        for allowed in self.allowed_commands:
            allowed_tokens = allowed.split()
            if tokens[: len(allowed_tokens)] == allowed_tokens:
                return tokens
        raise SafetyViolation(f"Comando no incluido en la whitelist: {tokens[0]}")

    # ----------------------------------------------------------------- arbol

    def iter_tree(self, workspace: Path) -> list[str]:
        """Lista acotada de archivos del workspace (rutas relativas, ordenadas)."""
        files: list[str] = []
        stack = [workspace]
        while stack and len(files) < self.max_tree_files:
            current = stack.pop()
            try:
                entries = sorted(current.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
            except (PermissionError, OSError):
                continue
            for entry in entries:
                if entry.name in self.excluded_dirs or entry.name.startswith("."):
                    continue
                if entry.is_dir():
                    stack.append(entry)
                elif len(files) < self.max_tree_files:
                    files.append(entry.relative_to(workspace).as_posix())
        return sorted(files)
