from __future__ import annotations

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.config import Settings
from app.domain.interfaces import LLMClient
from app.infrastructure.parsers.pdf_parser import PdfParser
from app.infrastructure.parsers.text_splitter import TextSplitter
from app.infrastructure.vector_db.chroma_client import ChromaVectorClient


TOPIC_COLLECTION_MAP = {
    "base de datos": "bases_datos",
    "bases de datos": "bases_datos",
    "cyberseguridad": "ciberseguridad",
    "ciberseguridad": "ciberseguridad",
    "programacion": "programacion",
    "programación": "programacion",
    "ui": "ui_ux",
    "ux": "ui_ux",
    "redes": "redes_ciberseguridad",
}


@dataclass(frozen=True)
class IngestionStats:
    files_processed: int
    chunks_created: int
    duplicates_skipped: int
    errors: list[str]


class IngestionService:
    def __init__(
        self,
        settings: Settings,
        llm_client: LLMClient,
        vector_client: ChromaVectorClient,
        pdf_parser: PdfParser | None = None,
        splitter: TextSplitter | None = None,
    ) -> None:
        self.settings = settings
        self.llm_client = llm_client
        self.vector_client = vector_client
        self.pdf_parser = pdf_parser or PdfParser()
        self.splitter = splitter or TextSplitter()

    def ingest(self, target_path: str | None = None, collection: str | None = None, topic: str | None = None, limit_files: int | None = None) -> IngestionStats:
        root = self.settings.rag_source_path
        target = Path(target_path) if target_path else root
        if not target.exists():
            return IngestionStats(0, 0, 0, [f"Path not found: {target}"])

        supported = {".pdf", ".md", ".txt"}
        if target.is_file() and target.suffix.lower() in supported:
            files = [target]
        else:
            files = sorted(p for p in target.rglob("*") if p.suffix.lower() in supported)
        if limit_files:
            files = files[:limit_files]

        files_processed = 0
        chunks_created = 0
        duplicates_skipped = 0
        errors: list[str] = []

        for file in files:
            try:
                inferred_collection = collection or self._infer_collection(file, root)
                inferred_topic = topic or inferred_collection
                created, skipped = self._ingest_file(file, inferred_collection, inferred_topic)
                chunks_created += created
                duplicates_skipped += skipped
                files_processed += 1
            except Exception as exc:
                errors.append(f"{file}: {exc}")

        return IngestionStats(files_processed, chunks_created, duplicates_skipped, errors)

    def _ingest_file(self, file: Path, collection: str, topic: str) -> tuple[int, int]:
        ids: list[str] = []
        documents: list[str] = []
        embeddings: list[list[float]] = []
        metadatas: list[dict[str, Any]] = []
        now = datetime.now(timezone.utc).isoformat()

        for page_number, text in self._iter_pages(file):
            for chunk_index, chunk in enumerate(self.splitter.split(text)):
                chunk_hash = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
                ids.append(f"{collection}:{chunk_hash}")
                documents.append(chunk)
                embeddings.append(self.llm_client.embed(self.settings.ollama_embed_model, chunk))
                metadatas.append(
                    {
                        "source": file.name,
                        "path": str(file),
                        "filename": file.name,
                        "topic": topic,
                        "collection": collection,
                        "page": page_number,
                        "chunk_index": chunk_index,
                        "hash": chunk_hash,
                        "ingested_at": now,
                    }
                )

        inserted = self.vector_client.add_documents(collection, ids, documents, embeddings, metadatas)
        return inserted, max(0, len(ids) - inserted)

    def _iter_pages(self, file: Path):
        """Genera (numero_pagina, texto) para PDF, Markdown o texto plano."""
        if file.suffix.lower() == ".pdf":
            for page in self.pdf_parser.extract_pages(file):
                yield page.page, page.text
            return
        text = file.read_text(encoding="utf-8", errors="replace")
        yield 1, text

    def _infer_collection(self, file: Path, root: Path) -> str:
        try:
            relative = file.relative_to(root)
            key = relative.parts[0].lower()
        except ValueError:
            key = file.parent.name.lower()
        return TOPIC_COLLECTION_MAP.get(key, self._sanitize_collection(key))

    def _sanitize_collection(self, value: str) -> str:
        safe = "".join(char.lower() if char.isalnum() else "_" for char in value)
        while "__" in safe:
            safe = safe.replace("__", "_")
        return safe.strip("_") or "general"
