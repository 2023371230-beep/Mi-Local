from app.application.router.query_router import QueryRouter
from app.config import get_settings
from app.domain.schemas import ChatRequest


def route(message: str, mode: str = "auto") -> str:
    return QueryRouter(get_settings()).route(ChatRequest(message=message, mode=mode)).skill_name


def test_router_respects_manual_mode():
    assert route("hola", mode="programacion") == "skill_programacion"


def test_router_programming():
    assert route("Tengo un error en React") == "skill_programacion"


def test_router_ui_ux():
    assert route("Mejora colores y contraste WCAG") == "skill_ui_ux"


def test_router_cybersecurity():
    assert route("Explica OWASP y hardening") == "skill_ciberseguridad"


def test_router_database():
    assert route("Optimiza una query PostgreSQL con indice") == "skill_bases_datos"


def test_router_rag():
    assert route("Segun mis documentos explica esto") == "skill_rag_local"


def test_router_web():
    assert route("Busca en web lo ultimo de ciberseguridad 2026") == "skill_web_search"
