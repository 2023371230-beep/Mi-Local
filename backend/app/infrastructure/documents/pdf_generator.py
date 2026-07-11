from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, Preformatted, SimpleDocTemplate, Spacer

from app.infrastructure.documents.md_blocks import parse_blocks

_STYLES = getSampleStyleSheet()
_CODE_STYLE = ParagraphStyle(
    "CodeBlock",
    parent=_STYLES["Code"],
    fontSize=8,
    leading=10,
    backColor="#f4f4f6",
    borderPadding=6,
)


def markdown_to_pdf(markdown_text: str, path: Path) -> None:
    doc = SimpleDocTemplate(
        str(path), pagesize=letter,
        leftMargin=2.2 * cm, rightMargin=2.2 * cm, topMargin=2 * cm, bottomMargin=2 * cm,
    )
    story = []
    bullets: list[str] = []
    numbers: list[str] = []

    def flush_lists() -> None:
        nonlocal bullets, numbers
        if bullets:
            story.append(ListFlowable([ListItem(Paragraph(escape(b), _STYLES["BodyText"])) for b in bullets], bulletType="bullet"))
            bullets = []
        if numbers:
            story.append(ListFlowable([ListItem(Paragraph(escape(n), _STYLES["BodyText"])) for n in numbers], bulletType="1"))
            numbers = []

    for block in parse_blocks(markdown_text):
        if block.kind == "bullet":
            bullets.append(block.text)
            continue
        if block.kind == "numbered":
            numbers.append(block.text)
            continue
        flush_lists()
        if block.kind == "heading1":
            story.append(Paragraph(escape(block.text), _STYLES["Title"]))
            story.append(Spacer(1, 8))
        elif block.kind == "heading2":
            story.append(Spacer(1, 10))
            story.append(Paragraph(escape(block.text), _STYLES["Heading2"]))
        elif block.kind == "heading3":
            story.append(Paragraph(escape(block.text), _STYLES["Heading3"]))
        elif block.kind == "code":
            story.append(Preformatted(block.text, _CODE_STYLE))
            story.append(Spacer(1, 6))
        else:
            story.append(Paragraph(escape(block.text), _STYLES["BodyText"]))
            story.append(Spacer(1, 4))
    flush_lists()
    doc.build(story)
