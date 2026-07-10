from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


@dataclass(frozen=True)
class PageText:
    page: int
    text: str


class PdfParser:
    def extract_pages(self, path: Path) -> list[PageText]:
        reader = PdfReader(str(path))
        pages: list[PageText] = []
        for index, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
            if normalized:
                pages.append(PageText(page=index, text=normalized))
        return pages
