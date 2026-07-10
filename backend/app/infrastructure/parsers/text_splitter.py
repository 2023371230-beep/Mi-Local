from __future__ import annotations


class TextSplitter:
    def __init__(self, chunk_size: int = 1000, overlap: int = 200) -> None:
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text: str) -> list[str]:
        clean = " ".join(text.split())
        if not clean:
            return []
        if len(clean) <= self.chunk_size:
            return [clean]

        chunks: list[str] = []
        start = 0
        while start < len(clean):
            hard_end = min(start + self.chunk_size, len(clean))
            end = self._find_soft_boundary(clean, start, hard_end)
            chunk = clean[start:end].strip()
            if chunk:
                chunks.append(chunk)
            if end >= len(clean):
                break
            start = max(0, end - self.overlap)
        return chunks

    def _find_soft_boundary(self, text: str, start: int, hard_end: int) -> int:
        if hard_end >= len(text):
            return len(text)
        minimum = start + int(self.chunk_size * 0.65)
        candidates = [text.rfind(mark, minimum, hard_end) for mark in [". ", "; ", ": ", " "]]
        boundary = max(candidates)
        return boundary + 1 if boundary > minimum else hard_end
