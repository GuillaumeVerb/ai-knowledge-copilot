from datetime import date
from typing import Optional

from backend.models.query import QueryFilters, SourceSnippet
from backend.repositories.documents_repo import DocumentsRepository
from backend.retrieval.reranker import KeywordOverlapReranker
from backend.retrieval.vector_store import VectorStore


class RetrievalService:
    def __init__(
        self,
        *,
        vector_store: VectorStore,
        documents_repository: Optional[DocumentsRepository] = None,
        reranker: Optional[KeywordOverlapReranker] = None,
        default_top_k: int = 6,
        fetch_k: int = 12,
    ):
        self.vector_store = vector_store
        self.documents_repository = documents_repository
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
        semantic_results = self.vector_store.search(
            query,
            top_k=max(top_k, self.fetch_k),
            filters={"document_ids": filters.document_ids, "tags": filters.tags},
        )
        semantic_results = [
            result
            for result in semantic_results
            if self._matches_filters(str(result["metadata"].get("document_id")), filters)
        ]
        raw_results = self._merge_results(
            query=query,
            semantic_results=semantic_results,
            filters=filters,
            top_k=max(top_k, self.fetch_k),
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

    def _merge_results(
        self,
        *,
        query: str,
        semantic_results: list[dict],
        filters: QueryFilters,
        top_k: int,
    ) -> list[dict]:
        lexical_results = self._lexical_search(query=query, filters=filters, top_k=top_k)
        semantic_scores = self._normalize_scores(semantic_results)
        lexical_scores = self._normalize_scores(lexical_results)

        merged: dict[str, dict] = {}
        for result in semantic_results:
            chunk_id = str(result["metadata"].get("chunk_id", result["id"]))
            merged[chunk_id] = dict(result)
            merged[chunk_id]["score"] = 0.65 * semantic_scores.get(chunk_id, 0.0)

        for result in lexical_results:
            chunk_id = str(result["metadata"].get("chunk_id", result["id"]))
            entry = merged.get(chunk_id, dict(result))
            entry["score"] = entry.get("score", 0.0) + 0.35 * lexical_scores.get(chunk_id, 0.0)
            merged[chunk_id] = entry

        ordered = sorted(merged.values(), key=lambda item: item["score"], reverse=True)
        return ordered[:top_k]

    def _lexical_search(
        self,
        *,
        query: str,
        filters: QueryFilters,
        top_k: int,
    ) -> list[dict]:
        if self.documents_repository is None:
            return []
        query_terms = set(self._tokenize(query))
        if not query_terms:
            return []
        results = []
        for chunk in self.documents_repository.list_all_chunks():
            document = self.documents_repository.get_document(chunk.document_id)
            if not self._document_matches(document, filters):
                continue
            chunk_terms = set(self._tokenize(chunk.text))
            overlap = len(query_terms & chunk_terms)
            if overlap == 0:
                continue
            results.append(
                {
                    "id": chunk.id,
                    "score": float(overlap),
                    "text": chunk.text,
                    "metadata": {
                        "document_id": document.id,
                        "document_name": document.original_filename,
                        "chunk_id": chunk.id,
                        "page_number": chunk.page_number,
                        "section_title": chunk.section_title,
                        "tags": document.tags,
                    },
                }
            )
        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_k]

    def _normalize_scores(self, results: list[dict]) -> dict[str, float]:
        if not results:
            return {}
        max_score = max(float(result["score"]) for result in results) or 1.0
        min_score = min(float(result["score"]) for result in results)
        if max_score == min_score:
            return {
                str(result["metadata"].get("chunk_id", result["id"])): 1.0
                for result in results
            }
        return {
            str(result["metadata"].get("chunk_id", result["id"])): (float(result["score"]) - min_score) / (max_score - min_score)
            for result in results
        }

    def _tokenize(self, text: str) -> list[str]:
        return [token.lower() for token in text.split() if len(token) > 2]

    def _matches_filters(self, document_id: str, filters: QueryFilters) -> bool:
        if self.documents_repository is None:
            return True
        try:
            document = self.documents_repository.get_document(document_id)
        except KeyError:
            return False
        return self._document_matches(document, filters)

    def _document_matches(self, document, filters: QueryFilters) -> bool:
        if filters.document_ids and document.id not in filters.document_ids:
            return False
        if filters.tags and not any(tag in document.tags for tag in filters.tags):
            return False
        if filters.categories and document.category not in filters.categories:
            return False
        if filters.date_from and not self._date_at_or_after(document.document_date, filters.date_from):
            return False
        if filters.date_to and not self._date_at_or_before(document.document_date, filters.date_to):
            return False
        return True

    def _date_at_or_after(self, value: Optional[date], threshold: date) -> bool:
        return value is not None and value >= threshold

    def _date_at_or_before(self, value: Optional[date], threshold: date) -> bool:
        return value is not None and value <= threshold
