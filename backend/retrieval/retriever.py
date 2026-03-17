from typing import Optional

from backend.models.query import QueryFilters, SourceSnippet
from backend.retrieval.reranker import KeywordOverlapReranker
from backend.retrieval.vector_store import VectorStore


class RetrievalService:
    def __init__(
        self,
        *,
        vector_store: VectorStore,
        reranker: Optional[KeywordOverlapReranker] = None,
        default_top_k: int = 6,
        fetch_k: int = 12,
    ):
        self.vector_store = vector_store
        self.reranker = reranker
        self.default_top_k = default_top_k
        self.fetch_k = fetch_k

    def retrieve(
        self,
        query: str,
        *,
        filters: Optional[QueryFilters] = None,
        top_k: Optional[int] = None,
        use_reranking: bool = False,
    ) -> list[SourceSnippet]:
        filters = filters or QueryFilters()
        top_k = top_k or self.default_top_k
        raw_results = self.vector_store.search(
            query,
            top_k=max(top_k, self.fetch_k),
            filters={"document_ids": filters.document_ids, "tags": filters.tags},
        )
        if use_reranking and self.reranker:
            raw_results = self.reranker.rerank(query, raw_results, top_k=top_k)
        else:
            raw_results = raw_results[:top_k]
        return [
            SourceSnippet(
                document_id=str(result["metadata"].get("document_id")),
                document_name=result["metadata"].get("document_name", "Unknown"),
                chunk_id=str(result["metadata"].get("chunk_id", result["id"])),
                excerpt=result["text"],
                page_number=result["metadata"].get("page_number"),
                section_title=result["metadata"].get("section_title"),
                score=float(result["score"]),
            )
            for result in raw_results
        ]
