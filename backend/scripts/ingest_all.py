from __future__ import annotations

from app.config import get_settings
from app.application.services.ingestion_service import IngestionService
from app.infrastructure.ollama.ollama_client import OllamaClient
from app.infrastructure.vector_db.chroma_client import ChromaVectorClient


def main() -> None:
    settings = get_settings()
    service = IngestionService(
        settings=settings,
        llm_client=OllamaClient(settings.ollama_base_url),
        vector_client=ChromaVectorClient(settings.chroma_path),
    )
    stats = service.ingest()
    print(stats)


if __name__ == "__main__":
    main()
