from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from app.application.services.document_service import DocumentService
from app.config import Settings
from app.infrastructure.documents.docx_generator import markdown_to_docx
from app.infrastructure.documents.html_generator import markdown_to_html
from app.infrastructure.documents.md_blocks import parse_blocks
from app.infrastructure.documents.pdf_generator import markdown_to_pdf

SAMPLE_MD = """# Titulo

## Seccion uno

Parrafo con **negritas** y `codigo`.

- item uno
- item dos

1. paso uno
2. paso dos

```python
print("hola")
```
"""


def test_parse_blocks_covers_structures():
    kinds = [block.kind for block in parse_blocks(SAMPLE_MD)]
    assert kinds == [
        "heading1", "heading2", "paragraph", "bullet", "bullet",
        "numbered", "numbered", "code",
    ]


def test_html_generator_produces_document():
    html = markdown_to_html(SAMPLE_MD, "Titulo")
    assert "<h1" in html and "<li>item uno</li>" in html and "print" in html


def test_docx_generator_writes_file(tmp_path: Path):
    out = tmp_path / "doc.docx"
    markdown_to_docx(SAMPLE_MD, out)
    assert out.exists() and out.stat().st_size > 1000


def test_pdf_generator_writes_file(tmp_path: Path):
    out = tmp_path / "doc.pdf"
    markdown_to_pdf(SAMPLE_MD, out)
    assert out.exists() and out.read_bytes()[:4] == b"%PDF"


class FakeLLM:
    def health(self):
        return True

    def list_models(self):
        return []

    def chat(self, model: str, messages: list[dict[str, str]], options: dict[str, Any] | None = None) -> str:
        return "# Reporte\n\n## Resumen ejecutivo\n\nTodo bien.\n"

    def embed(self, model: str, text: str) -> list[float]:
        return [0.0]


class FakeRag:
    def query(self, message, collection, top_k=5):
        return []


def make_service(tmp_path: Path) -> DocumentService:
    settings = Settings(documents_output_dir=tmp_path / "outputs")
    return DocumentService(settings=settings, llm_client=FakeLLM(), rag_service=FakeRag())


def test_document_service_generates_all_formats(tmp_path: Path):
    service = make_service(tmp_path)
    for fmt in ("md", "html", "docx", "pdf"):
        result = service.generate("reporte_tecnico", "Mi Reporte", "corto", output_format=fmt)
        assert result["filename"].endswith(f".{fmt}")
        assert (tmp_path / "outputs" / result["filename"]).exists()
        assert "Resumen ejecutivo" in result["markdown"]


def test_document_service_rejects_bad_type_and_format(tmp_path: Path):
    service = make_service(tmp_path)
    with pytest.raises(ValueError):
        service.generate("novela", "x", "y")
    with pytest.raises(ValueError):
        service.generate("readme", "x", "y", output_format="pptx")


def test_download_resolution_blocks_traversal(tmp_path: Path):
    service = make_service(tmp_path)
    service.generate("readme", "seguro", "z", output_format="md")
    with pytest.raises(FileNotFoundError):
        service.resolve_output("../secreto.txt")
    with pytest.raises(FileNotFoundError):
        service.resolve_output("..\\secreto.txt")
