"""Ingesta por lotes de PDFs pesados (TASK-0001).

CLI directo a Chroma/Ollama (sin HTTP): evita el timeout de 1h del endpoint /ingest.

Uso:
    .\\.venv\\Scripts\\python.exe .\\scripts\\ingest_heavy.py --manifest manifest.json
    .\\.venv\\Scripts\\python.exe .\\scripts\\ingest_heavy.py --file "C:\\...\\doc.pdf" [--pages 100-250]
    .\\.venv\\Scripts\\python.exe .\\scripts\\ingest_heavy.py --outline "C:\\...\\doc.pdf"  # ver capitulos

Manifest JSON: lista de objetos {"path": str, "pages": "ini-fin" opcional, "collection": str opcional}.
Checkpoint: JSONL en RAG/_metadata/; los archivos con status=done se saltan al relanzar.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from pypdf import PdfReader  # noqa: E402

from app.application.services.ingestion_service import IngestionService  # noqa: E402
from app.config import get_settings  # noqa: E402
from app.infrastructure.ollama.ollama_client import OllamaClient  # noqa: E402
from app.infrastructure.vector_db.chroma_client import ChromaVectorClient  # noqa: E402

BATCH_PAGES = 50
BATCH_PAUSE_S = 1.0


def load_checkpoint(log_path: Path) -> set[str]:
    """Claves (path|pages) ya completadas en corridas anteriores."""
    done: set[str] = set()
    if log_path.exists():
        for line in log_path.read_text(encoding="utf-8").splitlines():
            try:
                record = json.loads(line)
            except ValueError:
                continue
            if record.get("status") == "done":
                done.add(record.get("key", ""))
    return done


def append_log(log_path: Path, record: dict) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def parse_pages(spec: str | None, total: int) -> tuple[int, int]:
    """'100-250' -> (100, 250) acotado a [1, total]. Sin spec: todo el documento."""
    if not spec:
        return 1, total
    start_s, _, end_s = spec.partition("-")
    start = max(1, int(start_s))
    end = min(total, int(end_s or total))
    if start > end:
        raise ValueError(f"Rango de paginas invalido: {spec}")
    return start, end


def ingest_pdf_batched(
    service: IngestionService,
    path: Path,
    collection: str,
    pages: str | None,
    log_path: Path,
    batch_pages: int = BATCH_PAGES,
) -> dict:
    """Ingesta un PDF en lotes de paginas usando el pipeline dedup-antes-de-embeber."""
    reader = PdfReader(str(path))
    total = len(reader.pages)
    start, end = parse_pages(pages, total)
    now = datetime.now(timezone.utc).isoformat()

    chunks_created = 0
    duplicates = 0
    errors: list[str] = []
    batch_start = start
    while batch_start <= end:
        batch_end = min(batch_start + batch_pages - 1, end)
        t0 = time.perf_counter()
        try:
            # Troceo + hash por pagina del lote (mismo esquema de ids que /ingest).
            pending: list[tuple[str, str, dict]] = []
            for page_number in range(batch_start, batch_end + 1):
                text = reader.pages[page_number - 1].extract_text() or ""
                normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
                if not normalized:
                    continue
                for chunk_index, chunk in enumerate(service.splitter.split(normalized)):
                    import hashlib

                    chunk_hash = hashlib.sha256(chunk.encode("utf-8")).hexdigest()
                    pending.append(
                        (
                            f"{collection}:{chunk_hash}",
                            chunk,
                            {
                                "source": path.name,
                                "path": str(path),
                                "filename": path.name,
                                "topic": collection,
                                "collection": collection,
                                "page": page_number,
                                "chunk_index": chunk_index,
                                "hash": chunk_hash,
                                "ingested_at": now,
                            },
                        )
                    )
            if pending:
                all_ids = [item[0] for item in pending]
                existing = service.vector_client.existing_ids(collection, all_ids)
                new_items = [item for item in pending if item[0] not in existing]
                duplicates += len(pending) - len(new_items)
                if new_items:
                    # Lotes de 32 textos por peticion: amortiza HTTP y la cola de Ollama.
                    embeddings: list[list[float]] = []
                    embed_fn = getattr(service.llm_client, "embed_batch", None)
                    if callable(embed_fn):
                        for i in range(0, len(new_items), 32):
                            embeddings.extend(
                                embed_fn(
                                    service.settings.ollama_embed_model,
                                    [item[1] for item in new_items[i : i + 32]],
                                )
                            )
                    else:
                        embeddings = [
                            service.llm_client.embed(service.settings.ollama_embed_model, item[1])
                            for item in new_items
                        ]
                    inserted = service.vector_client.add_documents(
                        collection,
                        [i[0] for i in new_items],
                        [i[1] for i in new_items],
                        embeddings,
                        [i[2] for i in new_items],
                    )
                    chunks_created += inserted
        except Exception as exc:  # noqa: BLE001 - registrar y continuar con el siguiente lote
            errors.append(f"paginas {batch_start}-{batch_end}: {exc}")
        elapsed = time.perf_counter() - t0
        print(
            f"  [{path.name}] paginas {batch_start}-{batch_end}/{end} "
            f"chunks+={chunks_created} dup={duplicates} err={len(errors)} ({elapsed:.0f}s)",
            flush=True,
        )
        append_log(
            log_path,
            {
                "at": datetime.now(timezone.utc).isoformat(),
                "status": "batch",
                "file": path.name,
                "pages": f"{batch_start}-{batch_end}",
                "chunks": chunks_created,
                "duplicates": duplicates,
                "errors": errors[-1:] if errors else [],
                "seconds": round(elapsed, 1),
            },
        )
        batch_start = batch_end + 1
        time.sleep(BATCH_PAUSE_S)

    return {"chunks": chunks_created, "duplicates": duplicates, "errors": errors, "pages": f"{start}-{end}"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", help="JSON con lista de {path, pages?, collection?}")
    parser.add_argument("--file", action="append", default=[], help="PDF individual (repetible)")
    parser.add_argument("--pages", help="Rango ini-fin (solo con --file unico)")
    parser.add_argument("--outline", help="Imprime el indice de capitulos de un PDF y sale")
    parser.add_argument("--batch-pages", type=int, default=BATCH_PAGES)
    parser.add_argument("--log", default=None, help="Ruta del JSONL de checkpoint")
    args = parser.parse_args()

    if args.outline:
        reader = PdfReader(args.outline)
        print(f"{args.outline}: {len(reader.pages)} paginas")
        def walk(outline, depth=0):
            for item in outline:
                if isinstance(item, list):
                    walk(item, depth + 1)
                else:
                    try:
                        page = reader.get_destination_page_number(item) + 1
                    except Exception:  # noqa: BLE001
                        page = "?"
                    print(f"{'  ' * depth}p.{page}: {item.title}")
        walk(reader.outline)
        return 0

    entries: list[dict] = []
    if args.manifest:
        entries = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    for file_path in args.file:
        entries.append({"path": file_path, "pages": args.pages})
    if not entries:
        parser.error("se requiere --manifest o --file")

    settings = get_settings()
    service = IngestionService(
        settings=settings,
        llm_client=OllamaClient(settings.ollama_base_url, timeout=settings.ollama_timeout),
        vector_client=ChromaVectorClient(settings.chroma_path),
    )
    stamp = datetime.now().strftime("%Y-%m-%d")
    log_path = Path(args.log) if args.log else (settings.rag_source_path / "_metadata" / f"rag_ingest_heavy_{stamp}.jsonl")
    done = load_checkpoint(log_path)

    total_ok = 0
    for entry in entries:
        path = Path(entry["path"])
        key = f"{path}|{entry.get('pages') or 'all'}"
        if key in done:
            print(f"SKIP (checkpoint): {path.name}")
            continue
        if not path.exists():
            append_log(log_path, {"status": "error", "key": key, "file": path.name, "error": "no existe"})
            print(f"ERROR: no existe {path}")
            continue
        collection = entry.get("collection") or service._infer_collection(path, settings.rag_source_path)
        print(f"== {path.name} -> coleccion '{collection}'", flush=True)
        t0 = time.perf_counter()
        result = ingest_pdf_batched(service, path, collection, entry.get("pages"), log_path, args.batch_pages)
        append_log(
            log_path,
            {
                "at": datetime.now(timezone.utc).isoformat(),
                "status": "done" if not result["errors"] else "done_with_errors",
                "key": key,
                "file": path.name,
                "collection": collection,
                **result,
                "total_seconds": round(time.perf_counter() - t0, 1),
            },
        )
        total_ok += 1
    print(f"\nCompletados: {total_ok}/{len(entries)}. Log: {log_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
