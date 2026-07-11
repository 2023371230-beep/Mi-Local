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


def test_router_innocent_logs_not_cyber():
    """'logs de mi app' NO debe ir a ciberseguridad (patron antes sobre-ancho)."""
    assert route("como veo los logs de mi app en Next") != "skill_ciberseguridad"


def test_router_security_logs_go_cyber():
    assert route("analiza estos logs de seguridad sospechosos") == "skill_ciberseguridad"


def test_router_malware_goes_cyber():
    assert route("que es un ataque de phishing") == "skill_ciberseguridad"


class RouterFakeLLM:
    def __init__(self, answer):
        self.answer = answer
        self.calls = 0

    def health(self):
        return True

    def list_models(self):
        return []

    def chat(self, model, messages, options=None):
        self.calls += 1
        return self.answer

    def embed(self, model, text):
        return [0.0]


def test_router_pruned_patterns_no_false_positives():
    """Frases genericas ya no caen en skills tematicas por una palabra suelta."""
    assert route("como veo los logs de mi app en Next") != "skill_ciberseguridad"
    assert route("optimiza mi query de Chroma") != "skill_bases_datos"
    assert route("tuve un error raro ayer") != "skill_programacion"


def test_router_llm_second_pass_classifies():
    from app.application.router.query_router import QueryRouter
    from app.config import get_settings

    llm = RouterFakeLLM("bases_datos")
    router = QueryRouter(get_settings(), router_llm=llm)
    decision = router.route(ChatRequest(message="mi consulta tarda mucho en devolver filas"))
    assert decision.skill_name == "skill_bases_datos"
    assert decision.reason == "llm_router"
    assert llm.calls == 1


def test_router_llm_failure_falls_back_to_general():
    from app.application.router.query_router import QueryRouter
    from app.config import get_settings

    class BrokenLLM(RouterFakeLLM):
        def chat(self, model, messages, options=None):
            raise RuntimeError("timeout")

    router = QueryRouter(get_settings(), router_llm=BrokenLLM(""))
    decision = router.route(ChatRequest(message="hola que tal"))
    assert decision.skill_name == "skill_chat_general"


def test_router_ui_ux_uses_general_model_for_prose():
    from app.application.router.query_router import QueryRouter
    from app.config import get_settings

    settings = get_settings()
    router = QueryRouter(settings)
    prose = router.route(ChatRequest(message="mejora el contraste y la tipografia de mi interfaz"))
    assert prose.skill_name == "skill_ui_ux"
    assert prose.model_name == settings.ollama_general_model
    code = router.route(ChatRequest(message="dame el codigo css para mejorar el contraste de mi interfaz"))
    assert code.skill_name == "skill_ui_ux"
    assert code.model_name == settings.ollama_coder_model
