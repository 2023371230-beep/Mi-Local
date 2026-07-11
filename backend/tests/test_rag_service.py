from __future__ import annotations

from app.infrastructure.parsers.text_splitter import TextSplitter


def test_text_splitter_creates_overlap_chunks():
    text = " ".join(f"palabra{i}" for i in range(80))
    splitter = TextSplitter(chunk_size=120, overlap=20)

    chunks = splitter.split(text)

    assert len(chunks) > 1
    assert all(len(chunk) <= 120 for chunk in chunks)


def test_text_splitter_rejects_invalid_overlap():
    try:
        TextSplitter(chunk_size=100, overlap=100)
    except ValueError as exc:
        assert "overlap" in str(exc)
    else:
        raise AssertionError("E