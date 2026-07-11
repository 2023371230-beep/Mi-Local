from __future__ import annotations

from pathlib import Path
from typing import Any

import chromadb
from chromadb.api.models.Collection import Collection

from app.domain.interfaces import VectorDB


class ChromaVectorClient(VectorDB):
    def __init__(self, persist_path: Path | str) -> None:
        self.persist_path = Path(persist_path)
        self.persist_path.mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=str(self.persist_path))

    def health(self) -> bool:
        try:
            self.client.heartbeat()
            return True
        except Exception:
            return False

    def get_or_create_collection(self, name: str) -> Collection:
        return self.client.get_or_create_collection(name=name)

    def list_collections(self) -> list[str]:
        return [collection.name for collection in self.client.list_collections()]

    def delete_collection(self, name: str) -> None:
        self.client.delete_collection(name=name)

    def existing_ids(self, collection_name: str, ids: list[str]) -> set[str]:
        """IDs ya presentes en la coleccion (para dedup antes de embeber)."""
        if not ids:
            return set()
        collection = self.get_or_create_collection(collection_name)
        existing = collection.get(ids=ids, include=[])
        return set(existing.get("ids", []))

    def add_documents(
        self,
        collection_name: str,
        ids: list[str],
        documents: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, Any]],
    ) -> int:
        if not ids:
            return 0
        collection = self.get_or_create_collection(collection_name)
        existing = collection.get(ids=ids, include=[])
        existing_ids = set(existing.get("ids", []))

        new_ids: list[str] = []
        new_documents: list[str] = []
        new_embeddings: list[list[float]] = []
        new_metadatas: list[dict[str, Any]] = []

        for item_id, document, embedding, metadata in zip(ids, documents, embeddings, metadatas):
            if item_id in existing_ids:
                continue
            new_ids.append(item_id)
            new_documents.append(document)
            new_embeddings.append(embedding)
            new_metadatas.append(metadata)

        if not new_ids:
            return 0

        collection.add(
            ids=new_ids,
            documents=new_documents,
            embeddings=new_embeddings,
            metadatas=new_metadatas,
        )
        return len(new_ids)

    def query(
        self,
        collection_name: str,
        query_embedding: list[float],
        top_k: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        # get (no create): consultar una coleccion inexistente no debe crearla vacia.
        try:
            collection = self.client.get_collection(name=collection_name)
        except Exception:
            return []
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        items: list[dict[str, Any]] = []
        ids = results.get("ids", [[]])[0]
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        for item_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
            items.append(
                {
                    "id": item_id,
                    "document": document,
                    "metadata": metadata or {},
                    "distance": float(distance),
                }
            )
        return items
