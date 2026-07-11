from __future__ import annotations

import re
from dataclasses import dataclass

_INLINE_MARKS = re.compile(r"\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`")


@dataclass(frozen=True)
class Block:
    kind: str  # heading1|heading2|heading3|paragraph|bullet|numbered|code
    text: str


def strip_inline(text: str) -> str:
    """Quita **negritas**, *cursivas* y `code` para renderers planos (docx/pdf)."""
    return _INLINE_MARKS.sub(lambda m: m.group(1) or m.group(2) or m.group(3) or "", text)


def parse_blocks(markdown_text: str) -> list[Block]:
    """Parser minimo de Markdown a bloques para DOCX/PDF.

    Cubre lo que generan las plantillas: encabezados, parrafos, listas y codigo.
    No pretende ser un parser completo de Markdown.
    """
    blocks: list[Block] = []
    lines = (markdown_text or "").splitlines()
    index = 0
    paragraph: list[str] = []

    def flush_paragraph() -> None:
        if paragraph:
            blocks.append(Block("paragraph", strip_inline(" ".join(paragraph).strip())))
            paragraph.clear()

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if stripped.startswith("```"):
            flush_paragraph()
            code_lines: list[str] = []
            index += 1
            while index < len(lines) and not lines[index].strip().startswith("```"):
                code_lines.append(lines[index])
                index += 1
            blocks.append(Block("code", "\n".join(code_lines)))
        elif stripped.startswith("### "):
            flush_paragraph()
            blocks.append(Block("heading3", strip_inline(stripped[4:])))
        elif stripped.startswith("## "):
            flush_paragraph()
            blocks.append(Block("heading2", strip_inline(stripped[3:])))
        elif stripped.startswith("# "):
            flush_paragraph()
            blocks.append(Block("heading1", strip_inline(stripped[2:])))
        elif re.match(r"^[-*] ", stripped):
            flush_paragraph()
            blocks.append(Block("bullet", strip_inline(stripped[2:])))
        elif re.match(r"^\d+[.)] ", stripped):
            flush_paragraph()
            blocks.append(Block("numbered", strip_inline(re.sub(r"^\d+[.)] ", "", stripped))))
        elif not stripped:
            flush_paragraph()
        else:
            paragraph.append(stripped)
        index += 1
    flush_paragraph()
    return blocks
