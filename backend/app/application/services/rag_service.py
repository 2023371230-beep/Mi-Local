from __future__ import annotations

from app.config import Settings
from app.domain.interfaces import LLMClient
from app.infrastructure.vector_db.chroma_client import ChromaVectorClient


class RagService:
    def __init__(self, settings: Settings, llm_client: LLMClient, vector_client: ChromaVectorClient) -> None:
        self.settings = settings
        self.llm_client = llm_client
        self.vector_client = vector_client

    def list_collections(self) -> list[str]:
        return self.vector_client.list_collections()

    def query(self, message: str, collection: str, top_k: int = 5) -> list[dict]:
        query_embedding = self.llm_client.embed(self.settings.ollama_embed_model, message)
        return self.vector_client.query(collection, query_embedding, top_k=top_k)

    def answer(self, message: str, collection: str, top_k: int = 5) -> tuple[str, list[dict]]:
        results = self.query(message, collection, top_k)
        if not results:
            return "No encontre contexto local util en la coleccion indicada.", []

        context_blocks = []
        sources = []
        for index, item in enumerate(results, start=1):
            metadata = item.get("metadata", {})
            context_blocks.append(
                f"[{index}] {metadata.get('filename')} pagina {metadata.get('page')} chunk {metadata.get('chunk_index')}: {item.get('document')}"
            )
            sources.append(
                {
                    "source": metadata.get("source") or metadata.get("filename") or "local",
                    "path": metadata.get("path"),
                    "filename": metadata.get("filename"),
                    "page": metadata.get("page"),
                    "chunk_index": metadata.get("chunk_index"),
                    "score": item.get("distance"),
                }
            )

        prompt = (
            "Responde usando solo el contexto local. Si el contexto no alcanza, dilo claramente.\n\n"
            f"Pregunta: {message}\n\nContexto:\n" + "\n\n".join(context_blocks)
        )
        answer = self.llm_client.chat(
            self.settings.ollama_general_model,
            [
                {"role": "system", "content": "Eres un asistente tecnico de RAG local. Cita filename, pagina y chunk cuando uses una fuente."},
                {"role": "user", "content": prompt},
            ],
            options={"temperature": 0.1, "num_ctx": 4096},
        )
        return answer, sources
