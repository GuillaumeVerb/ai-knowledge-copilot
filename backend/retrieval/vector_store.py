from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as rest


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        raise NotImplementedError


class VectorStore(ABC):
    @abstractmethod
    def upsert(self, items: list[dict[str, Any]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query: str,
        *,
        top_k: int,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        raise NotImplementedError

    @abstractmethod
    def delete_by_document_id(self, document_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def recreate(self, items: list[dict[str, Any]]) -> None:
        raise NotImplementedError


class QdrantVectorStore(VectorStore):
    def __init__(
        self,
        *,
        client: QdrantClient,
        collection_name: str,
        embedding_provider: EmbeddingProvider,
        vector_size: int = 1536,
    ):
        self.client = client
        self.collection_name = collection_name
        self.embedding_provider = embedding_provider
        self.vector_size = vector_size
        self._ensure_collection()

    def _ensure_collection(self) -> None:
        collections = [collection.name for collection in self.client.get_collections().collections]
        if self.collection_name in collections:
            return
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config=rest.VectorParams(size=self.vector_size, distance=rest.Distance.COSINE),
        )

    def upsert(self, items: list[dict[str, Any]]) -> None:
        if not items:
            return
        embeddings = self.embedding_provider.embed_documents([item["text"] for item in items])
        points = []
        for item, embedding in zip(items, embeddings):
            payload = dict(item["metadata"])
            payload["text"] = item["text"]
            points.append(rest.PointStruct(id=item["id"], vector=embedding, payload=payload))
        self.client.upsert(collection_name=self.collection_name, points=points)

    def search(
        self,
        query: str,
        *,
        top_k: int,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        query_vector = self.embedding_provider.embed_query(query)
        query_filter = self._build_filter(filters or {})
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            query_filter=query_filter,
            limit=top_k,
            with_payload=True,
        )
        return [
            {
                "id": point.id,
                "score": point.score,
                "text": point.payload.get("text", ""),
                "metadata": point.payload,
            }
            for point in results
        ]

    def delete_by_document_id(self, document_id: str) -> None:
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=rest.FilterSelector(
                filter=rest.Filter(
                    must=[
                        rest.FieldCondition(
                            key="document_id",
                            match=rest.MatchValue(value=document_id),
                        )
                    ]
                )
            ),
        )

    def recreate(self, items: list[dict[str, Any]]) -> None:
        self.client.delete_collection(self.collection_name)
        self._ensure_collection()
        self.upsert(items)

    def _build_filter(self, filters: dict[str, Any]) -> Optional[rest.Filter]:
        must_conditions: list[rest.FieldCondition] = []
        document_ids = filters.get("document_ids") or []
        tags = filters.get("tags") or []
        if document_ids:
            must_conditions.append(
                rest.FieldCondition(key="document_id", match=rest.MatchAny(any=document_ids))
            )
        if tags:
            must_conditions.append(rest.FieldCondition(key="tags", match=rest.MatchAny(any=tags)))
        if not must_conditions:
            return None
        return rest.Filter(must=must_conditions)


class InMemoryVectorStore(VectorStore):
    def __init__(self, embedding_provider: EmbeddingProvider):
        self.embedding_provider = embedding_provider
        self.items: dict[str, dict[str, Any]] = {}

    def upsert(self, items: list[dict[str, Any]]) -> None:
        for item, embedding in zip(
            items,
            self.embedding_provider.embed_documents([item["text"] for item in items]),
        ):
            self.items[item["id"]] = {**item, "embedding": embedding}

    def search(
        self,
        query: str,
        *,
        top_k: int,
        filters: Optional[dict[str, Any]] = None,
    ) -> list[dict[str, Any]]:
        filters = filters or {}
        query_embedding = self.embedding_provider.embed_query(query)
        scored: list[dict[str, Any]] = []
        for item in self.items.values():
            metadata = item["metadata"]
            if filters.get("document_ids") and metadata.get("document_id") not in filters["document_ids"]:
                continue
            if filters.get("tags"):
                tags = metadata.get("tags") or []
                if not any(tag in tags for tag in filters["tags"]):
                    continue
            score = self._cosine_similarity(query_embedding, item["embedding"])
            scored.append(
                {
                    "id": item["id"],
                    "score": score,
                    "text": item["text"],
                    "metadata": metadata,
                }
            )
        scored.sort(key=lambda entry: entry["score"], reverse=True)
        return scored[:top_k]

    def delete_by_document_id(self, document_id: str) -> None:
        self.items = {
            item_id: item
            for item_id, item in self.items.items()
            if item["metadata"].get("document_id") != document_id
        }

    def recreate(self, items: list[dict[str, Any]]) -> None:
        self.items = {}
        self.upsert(items)

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        numerator = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return numerator / (norm_a * norm_b)
