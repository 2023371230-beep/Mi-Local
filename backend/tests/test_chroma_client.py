from __future__ import annotations

from app.infrastructure.vector_db.chroma_client import ChromaVectorClient


def test_chroma_add_query_and_metadata(tmp_path):
    client = ChromaVectorClient(tmp_path / "chroma")
    collection_name = "test_collection"

    inserted = client.add_documents(
        collection_name=collection_name,
        ids=["doc-1", "doc-2", "doc-3"],
        documents=["redes ospf bgp", "seguridad owasp xss", "bases datos indice sql"],
        embeddings=[
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
        ],
        metadatas=[
            {"filename": "redes.pdf", "page": 1, "collection": collection_name},
            {"filename": "owasp.pdf", "page": 2, "collection": collection_name},
            {"filename": "sql.pdf", "page": 3, "collection": collection_name},
        ],
    )

    assert inserted == 3
    assert collection_name in client.list_collections()

    results = client.query(collection_name, [0.0, 1.0, 0.0], top_k=1)

    assert results[0]["metadata"]["filename"] == "owasp.pdf"
    assert results[0]["metadata"]["page"] == 2


def test_chroma_skips_duplicate_ids(tmp_path):
    client = ChromaVectorClient(tmp_path / "chroma")
    collection_name = "dedupe"

    first = client.add_documents(
        collection_name,
        ["same-id"],
        ["texto inicial"],
        [[1.0, 0.0]],
        [{"hash": "same-id"}],
    )
    second = client.add_documents(
        collection_name,
        ["same-id"],
        ["texto duplicado"],
        [[1.0, 0.0]],
        [{"hash": "same-id"}],
    )

    assert first == 1
    assert second == 0
