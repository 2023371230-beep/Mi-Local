from __future__ import annotations

import re


MODE_TO_SKILL = {
    "programacion": "skill_programacion",
    "ui_ux": "skill_ui_ux",
    "ciberseguridad": "skill_ciberseguridad",
    "bases_datos": "skill_bases_datos",
    "rag": "skill_rag_local",
    "web": "skill_web_search",
    "general": "skill_chat_general",
}

SKILL_COLLECTIONS = {
    "skill_programacion": "programacion",
    "skill_ui_ux": "ui_ux",
    "skill_ciberseguridad": "ciberseguridad",
    "skill_bases_datos": "bases_datos",
    "skill_rag_local": "general",
}

RAG_PATTERNS = [
    r"segun mis documentos",
    r"segun mi rag",
    r"busca en mis pdfs",
    r"mis apuntes",
    r"documentacion local",
]

WEB_PATTERNS = [
    r"\bactual\b",
    r"\b2026\b",
    r"\bultimo\b",
    r"\bultimos\b",
    r"\bhoy\b",
    r"\bnoticia\b",
    r"busca en web",
    r"internet",
]

PROGRAMMING_PATTERNS = [
    r"\breact\b",
    r"\bnode\b",
    r"\bpython\b",
    r"\bjava\b",
    r"\bphp\b",
    r"\bflutter\b",
    r"\bsql\b",
    r"\berror\b",
    r"\bcodigo\b",
    r"\bscript\b",
    r"\bapi\b",
]

UI_UX_PATTERNS = [
    r"colores?",
    r"tipografia",
    r"interfaz",
    r"diseno",
    r"\bui\b",
    r"\bux\b",
    r"mockup",
    r"botones?",
    r"contraste",
    r"wcag",
]

CYBER_PATTERNS = [
    r"owasp",
    r"nist",
    r"vulnerabilidad",
    r"hardening",
    r"\bataque\b",
    r"\bmalware\b",
    r"\bphishing\b",
    r"siem",
    r"\bxss\b",
    r"sql injection",
    r"pentest",
    r"\bcifrad",
    # "logs" solo enruta a ciber junto a contexto de seguridad, no cualquier log de app.
    r"logs? de seguridad",
    r"logs? sospechos",
]

DATABASE_PATTERNS = [
    r"postgresql",
    r"mysql",
    r"base de datos",
    r"\bquery\b",
    r"indice",
    r"normalizacion",
    r"trigger",
    r"schema",
]


def matches_any(message: str, patterns: list[str]) -> bool:
    normalized = _normalize(message)
    return any(re.search(pattern, normalized, flags=re.IGNORECASE) for patter