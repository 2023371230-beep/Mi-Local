from __future__ import annotations

import re
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path

from loguru import logger

from app.application.services.rag_service import RagService
from app.config import Settings
from app.domain.interfaces import LLMClient
from app.infrastructure.documents.docx_generator import markdown_to_docx
from app.infrastructure.documents.html_generator import markdown_to_html
from app.infrastructure.documents.pdf_generator import markdown_to_pdf

# Plantillas por tipo: estructura esperada que el modelo debe seguir.
DOCUMENT_TEMPLATES: dict[str, str] = {
    "reporte_tecnico": (
        "Estructura: # Titulo / ## Resumen ejecutivo / ## Contexto / ## Analisis "
        "/ ## Hallazgos / ## Recomendaciones / ## Conclusiones."
    ),
    "manual_usuario": (
        "Estructura: # Titulo / ## Introduccion / ## Requisitos / ## Primeros pasos "
        "/ ## Uso paso a paso (con listas numeradas) / ## Problemas comunes / ## Contacto."
    ),
    "manual_tecnico": (
        "Estructura: # Titulo / ## Arquitectura / ## Componentes / ## Instalacion "
        "/ ## Configuracion / ## Operacion / ## Troubleshooting."
    ),
    "documentacion_api": (
        "Estructura: # API / ## Autenticacion / ## Endpoints (uno por seccion ### METODO /ruta "
        "con parametros, ejemplo de request y de response en bloques de codigo) / ## Errores."
    ),
    "readme": (
        "Estructura: # Nombre / descripcion corta / ## Caracteristicas / ## Instalacion "
        "/ ## Uso (con ejemplos en bloques de codigo) / ## Estructura del proyecto / ## Licencia."
    ),
    "reporte_practica": (
        "Estructura: # Titulo / ## Objetivo / ## Marco teorico / ## Desarrollo "
        "/ ## Resultados / ## Conclusiones / ## Referencias."
    ),
    "requerimientos": (
        "Estructura: # Documento de requerimientos / ## Alcance / ## Requerimientos funcionales "
        "(lista RF-01, RF-02...) / ## Requerimientos no funcionales (RNF-01...) / ## Supuestos."
    ),
    "politica": (
        "Estructura: # Politica / ## Proposito / ## Alcance / ## Politica (numerada) "
        "/ ## Roles y responsabilidades / ## Cumplimiento / ## Revision."
    ),
    "checklist": "Estructura: # Titulo / secciones ## con listas de items '- [ ] item'.",
}

SUPPORTED_FORMATS = ("md", "html", "docx", "pdf")

_SYSTEM_PROMPT = (
    "Eres un redactor tecnico profesional. Generas documentos completos en Markdown, en espanol, "
    "listos para entregar. Sigue EXACTAMENTE la estructura indicada. Usa encabezados #/##/###, "
    "listas y bloques de codigo cuando aporten. Sin comentarios fuera del documento. "
    "Si se te da contexto de documentos del usuario, usalo y citalo en el texto donde aplique."
)


class DocumentService:
    def __init__(self, settings: Settings, llm_client: LLMClient, rag_service: RagService) -> None:
        self.settings = settings
        self.llm_client = llm_client
        self.rag_service = rag_service
        self.output_dir = Path(settings.documents_output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------- generacion

    def generate(
        self,
        doc_type: str,
        title: str,
        instructions: str,
        output_format: str = "md",
        use_rag: bool = False,
        collection: str | None = None,
    ) -> dict:
        if doc_type not in DOCUMENT_TEMPLATES:
            raise ValueError(f"Tipo de documento no soportado: {doc_type}. Opciones: {list(DOCUMENT_TEMPLATES)}")
        if output_format not in SUPPORTED_FORMATS:
            raise ValueError(f"Formato no soportado: {output_format}. Opciones: {list(SUPPORTED_FORMATS)}")

        started = time.perf_counter()
        context_block = ""
        rag_sources: list[dict] = []
        if use_rag and collection:
            results = self.rag_service.query(instructions or title, collection, top_k=4)
            relevant = [r for r in results if r.get("distance", 1.0) <= self.settings.rag_max_distance]
            if relevant:
                context_block = "\n\nContexto de los documentos del usuario:\n" + "\n".join(
                    f"[{i}] {r['metadata'].get('filename')}: {r['document'][:600]}"
                    for i, r in enumerate(relevant, start=1)
                )
                rag_sources = [
                    {
                        "filename": r["metadata"].get("filename"),
                        "page": r["metadata"].get("page"),
                        "score": r.get("distance"),
                    }
                    for r in relevant
                ]

        markdown_text = self.llm_client.chat(
            self.settings.ollama_general_model,
            [
                {"role": "system", "content": _SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Tipo de documento: {doc_type}\n"
                        f"{DOCUMENT_TEMPLATES[doc_type]}\n\n"
                        f"Titulo: {title}\n"
                        f"Indicaciones del usuario: {instructions}"
                        f"{context_block}"
                    ),
                },
            ],
            options={"temperature": 0.3, "num_ctx": 8192},
        )
        markdown_text = self._strip_fences(markdown_text)

        filename = self._build_filename(title, output_format)
        path = self.output_dir / filename
        self._render(markdown_text, output_format, path, title)

        latency_ms = int((time.perf_counter() - started) * 1000)
        logger.info("documento generado type={} format={} file={} latency_ms={}", doc_type, output_format, filename, latency_ms)
        return {
            "filename": filename,
            "format": output_format,
            "doc_type": doc_type,
            "markdown": markdown_text,
            "sources": rag_sources,
            "latency_ms": latency_ms,
        }

    # --------------------------------------------------------------- outputs

    def list_outputs(self) -> list[dict]:
        items = []
        for path in sorted(self.output_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
            if path.is_file():
                items.append(
                    {
                        "filename": path.name,
                        "size_bytes": path.stat().st_size,
                        "modified_at": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat(),
                    }
                )
        return items

    def resolve_output(self, filename: str) -> Path:
        # Sin traversal: el nombre debe resolver DENTRO de outputs/.
        candidate = (self.output_dir / filename).resolve()
        if candidate.parent != self.output_dir.resolve() or not candidate.is_file():
            raise FileNotFoundError(filename)
        return candidate

    # ----------------------------------------------------------------- utils

    def _render(self, markdown_text: str, output_format: str, path: Path, title: str) -> None:
        if output_format == "md":
            path.write_text(markdown_text, encoding="utf-8")
        elif output_format == "html":
            path.write_text(markdown_to_html(markdown_text, title), encoding="utf-8")
        elif output_format == "docx":
            markdown_to_docx(markdown_text, path)
        elif output_format == "pdf":
            markdown_to_pdf(markdown_text, path)

    def _strip_fences(self, text: str) -> str:
        cleaned = (text or "").strip()
        match = re.match(r"^```(?:markdown|md)?\n(.*)\n```$", cleaned, flags=re.DOTALL)
        return match.group(1) if match else cleaned

    def _build_filename(self, title: str, output_format: str) -> str:
        normalized = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
        slug = re.sub(r"[^a-zA-Z0-9]+", "-", normalized).strip("-").lower()[:60] or "documento"
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"{slug}-{stamp}.{output_format}"
