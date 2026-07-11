from __future__ import annotations

from pathlib import Path

from app.application.services.ingestion_service import IngestionService
from app.config import get_settings


class FakeLLM:
    def embed(self, model, text):
        return [0.1, 0.2, 0.3]


class FakeVectorClient:
    def __init__(self):
        self.calls = []

    def add_documents(self, collection, ids, documents, embeddings, metadatas):
        self.calls.append({"collection": collection, "ids": ids, "documents": documents, "metadatas": metadatas})
        return len(ids)

    def existing_ids(self, collection, ids):
        return set()


def test_ingest_markdown_file(tmp_path: Path):
    root = tmp_path / "RAG"
    (root / "Asistente").mkdir(parents=True)
    doc = root / "Asistente" / "guia.md"
    doc.write_text("# Titulo\n\nContenido de prueba para el RAG local.", encoding="utf-8")

    vector = FakeVectorClient()
    service = IngestionService(settings=get_settings(), llm_client=FakeLLM(), vector_client=vector)
    stats = service.ingest(target_path=str(doc), collection="asistente")

    assert stats.files_processed == 1
    assert stats.chunks_created >= 1
    assert not stats.errors
    assert vector.calls[0]["collection"] == "asistente"
    assert vector.calls[0]["metadatas"][0]["filename"] == "guia.md"
    assert vector.calls[0]["metadatas"][0]["page"] == 1


def test_ingest_discovers_md_and_txt_in_folder(tmp_path: Path):
    root = tmp_path / "RAG"
    sub = root / "Programacion"
    sub.mkdir(parents=True)
    (sub / "a.md").write_text("contenido markdown", encoding="utf-8")
    (sub / "b.txt").write_text("contenido texto", encoding="utf-8")
    (sub / "c.docx").write_text("no soportado", encoding="utf-8")

    vector = FakeVectorClient()
    service = IngestionService(settings=get_settings(), llm_client=FakeLLM(), vector_client=vector)
    stats = service.ingest(target_path=str(sub), collection="programacion")

    assert stats.files_processed == 2
    assert not stats.errors


def test_ingest_infers_collection_from_folder(tmp_path: Path):
    sub = tmp_path / "Asistente"
    sub.mkdir(parents=True)
    (sub / "doc.md").write_text("texto", encoding="utf-8")

    vector = FakeVectorClient()
    service = IngestionService(settings=get_settings(), llm_client=FakeLLM(), vector_client=vector)
    stats = service.ingest(target_path=str(sub))

    assert stats.files_processed == 1
    assert not stats.errors
    # la coleccion se infiere del nombre de la carpeta contenedora
    assert vector.calls[0]["collection"] == "asistente"
