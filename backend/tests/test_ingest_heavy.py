from __future__ import annotations

import json
import sys
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from ingest_heavy import ingest_pdf_batched, load_checkpoint, parse_pages  # noqa: E402

from app.application.services.ingestion_service import IngestionService
from app.config import Settings


class CountingLLM:
    def __init__(self):
        self.embed_calls = 0

    def health(self):
        return True

    def list_models(self):
        return []

    def chat(self, model, messages, options=None):
        return ""

    def embed(self, model, text):
        self.embed_calls += 1
        return [0.1, 0.2]


class MemoryVector:
    """Vector store en memoria con la misma interfaz que ChromaVectorClient."""

    def __init__(self):
        self.store: dict[str, dict] = {}

    def existing_ids(self, collection, ids):
        return {i for i in ids if i in self.store}

    def add_documents(self, collection, ids, documents, embeddings, metadatas):
        added = 0
        for item_id, doc, meta in zip(ids, documents, metadatas):
            if item_id not in self.store:
                self.store[item_id] = {"doc": doc, "meta": meta}
                added += 1
        return added


def make_pdf(path: Path, pages: int) -> None:
    pdf = canvas.Canvas(str(path), pagesize=letter)
    for number in range(1, pages + 1):
        pdf.drawString(72, 700, f"Pagina {number}: contenido tecnico de prueba numero {number}.")
        pdf.showPage()
    pdf.save()


def make_service(tmp_path: Path, llm: CountingLLM, vector: MemoryVector) -> IngestionService:
    settings = Settings(rag_source_path=tmp_path)
    return IngestionService(settings=settings, llm_client=llm, vector_client=vector)


def test_parse_pages_bounds():
    assert parse_pages(None, 120) == (1, 120)
    assert parse_pages("10-50", 120) == (10, 50)
    assert parse_pages("100-999", 120) == (100, 120)


def test_batched_ingest_processes_all_pages(tmp_path: Path):
    pdf = tmp_path / "libro.pdf"
    make_pdf(pdf, 12)
    llm, vector = CountingLLM(), MemoryVector()
    service = make_service(tmp_path, llm, vector)
    log = tmp_path / "log.jsonl"

    result = ingest_pdf_batched(service, pdf, "programacion", None, log, batch_pages=5)

    assert result["chunks"] == 12  # una pagina corta = un chunk
    assert result["errors"] == []
    assert llm.embed_calls == 12
    # 3 lotes (5+5+2) registrados
    batches = [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines()]
    assert len([b for b in batches if b["status"] == "batch"]) == 3


def test_dedup_does_not_reembed(tmp_path: Path):
    pdf = tmp_path / "doc.pdf"
    make_pdf(pdf, 4)
    llm, vector = CountingLLM(), MemoryVector()
    service = make_service(tmp_path, llm, vector)
    log = tmp_path / "log.jsonl"

    ingest_pdf_batched(service, pdf, "bases_datos", None, log, batch_pages=10)
    first_calls = llm.embed_calls
    result2 = ingest_pdf_batched(service, pdf, "bases_datos", None, log, batch_pages=10)

    assert llm.embed_calls == first_calls  # nada se re-embebe
    assert result2["duplicates"] == 4


def test_checkpoint_marks_done(tmp_path: Path):
    log = tmp_path / "log.jsonl"
    log.write_text(
        json.dumps({"status": "done", "key": "C:/x/doc.pdf|all"}) + "\n"
        + json.dumps({"status": "batch", "key": "otro"}) + "\n",
        encoding="utf-8",
    )
    done = load_checkpoint(log)
    assert "C:/x/doc.pdf|all" in done
    assert "otro" not in done
