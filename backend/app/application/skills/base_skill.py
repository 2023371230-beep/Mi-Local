from __future__ import annotations

from app.domain.interfaces import LLMClient
from app.domain.models import SkillResult
from app.domain.schemas import ChatRequest


class BaseSkill:
    name = "base_skill"
    description = "Base skill"
    default_model = ""
    system_prompt = "Eres un asistente tecnico."
    # Ejemplos few-shot opcionales: pares (pregunta, respuesta ideal). En modelos
    # locales chicos ensenan el formato esperado mejor que cualquier instruccion.
    few_shot: tuple[tuple[str, str], ...] = ()
    # Opciones de generacion por skill (se mezclan sobre los defaults).
    chat_options: dict[str, float | int] = {}

    def __init__(
        self,
        llm_client: LLMClient,
        model_name: str | None = None,
        rag_service=None,
        rag_collection: str | None = None,
    ) -> None:
        self.llm_client = llm_client
        self.default_model = model_name or self.default_model
        self.rag_service = rag_service
        self.rag_collection = rag_collection
        # Fuentes del ultimo build_messages (para run y para /chat/stream).
        self.last_rag_sources: list[dict] = []

    def _gather_rag_context(self, request: ChatRequest) -> tuple[str, list[dict]]:
        """RAG contextual: si la coleccion de la skill tiene material relevante, lo anexa.

        Vacio si no hay servicio, si el usuario desactivo RAG o si nada pasa el umbral.
        """
        if self.rag_service is None or not self.rag_collection or request.use_rag == "false":
            return "", []
        try:
            results = self.rag_service.query(request.message, self.rag_collection, top_k=3)
        except Exception:  # noqa: BLE001 - el RAG contextual nunca debe tumbar el chat
            return "", []
        threshold = self.rag_service.settings.rag_max_distance
        relevant = [r for r in results if r.get("distance", 1.0) <= threshold]
        if not relevant:
            return "", []
        blocks: list[str] = []
        sources: list[dict] = []
        for index, item in enumerate(relevant, start=1):
            meta = item.get("metadata", {})
            blocks.append(f"[{index}] {meta.get('filename')} p.{meta.get('page')}: {item.get('document')}")
            sources.append(
                {
                    "source": meta.get("source") or meta.get("filename") or "local",
                    "path": meta.get("path"),
                    "filename": meta.get("filename"),
                    "page": meta.get("page"),
                    "chunk_index": meta.get("chunk_index"),
                    "score": item.get("distance"),
                }
            )
        context = (
            "Contexto de los documentos del usuario (citalos por filename si los usas):\n"
            + "\n\n".join(blocks)
        )
        return context, sources

    # Regla comun a todas las skills: no adivinar cuando falta un dato critico.
    _CLARIFY_RULE = (
        "\nSi la peticion es ambigua en un punto que cambia la respuesta (version, stack, objetivo), "
        "haz UNA sola pregunta de aclaracion antes de responder; si puedes asumir lo mas comun, "
        "asumelo y dilo explicitamente."
    )

    def build_messages(self, request: ChatRequest) -> list[dict[str, str]]:
        system = self.system_prompt + self._CLARIFY_RULE
        messages: list[dict[str, str]] = [{"role": "system", "content": system}]
        for question, answer in self.few_shot:
            messages.append({"role": "user", "content": question})
            messages.append({"role": "assistant", "content": answer})
        context, sources = self._gather_rag_context(request)
        self.last_rag_sources = sources
        if context:
            messages.append({"role": "system", "content": context})
        messages.append({"role": "user", "content": request.message})
        return messages

    def run(self, request: ChatRequest) -> SkillResult:
        options: dict[str, float | int] = {"temperature": 0.2, "num_ctx": 4096}
        options.update(self.chat_options)
        answer = self.llm_client.chat(
            self.default_model,
            self.build_messages(request),
            options=options,
        )
        return SkillResult(
            answer=answer,
            skill_used=self.name,
            model_used=self.default_model,
            rag_used=bool(self.last_rag_sources),
            sources=self.last_rag_sources,
        )
