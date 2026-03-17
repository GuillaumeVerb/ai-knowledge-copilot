from __future__ import annotations

import logging
import re
import time

from backend.llm.answer_formatter import format_citations
from backend.llm.generator import LLMProvider
from backend.llm.prompts import build_query_prompt, build_summary_prompt
from backend.models.answer import DocumentSummaryResponse
from backend.models.query import CompareDocumentsRequest, QueryFilters, QueryRequest, QueryResponse, SourceSnippet
from backend.repositories.documents_repo import DocumentsRepository
from backend.repositories.qa_history_repo import QueryHistoryRepository
from backend.retrieval.retriever import RetrievalService


logger = logging.getLogger(__name__)


class QueryService:
    FALLBACK_STOPWORDS = {
        "what", "which", "with", "that", "from", "this", "there", "have", "will", "your",
        "about", "when", "where", "their", "they", "them", "then", "than", "also", "only",
        "based", "available", "document", "documents", "question", "answer", "using", "used",
        "after", "before", "must", "should", "could", "would", "does", "dont", "cant", "not",
        "are", "was", "were", "been", "being", "the", "and", "for", "but", "you", "our", "out",
        "who", "why", "how", "all", "any", "per", "one", "two", "three", "can", "has", "had",
        "its", "into", "over", "under", "each", "such", "just", "within", "across", "more",
        "most", "much", "many", "some", "same", "very", "like", "need", "needs", "required",
    }

    def __init__(
        self,
        *,
        retrieval_service: RetrievalService,
        llm_provider: LLMProvider,
        history_repository: QueryHistoryRepository,
        documents_repository: DocumentsRepository,
        enable_reranking: bool,
        max_summary_chunks: int,
    ):
        self.retrieval_service = retrieval_service
        self.llm_provider = llm_provider
        self.history_repository = history_repository
        self.documents_repository = documents_repository
        self.enable_reranking = enable_reranking
        self.max_summary_chunks = max_summary_chunks

    def answer_query(self, request: QueryRequest) -> QueryResponse:
        start = time.perf_counter()
        sources = self.retrieval_service.retrieve(
            request.question,
            filters=request.filters,
            top_k=request.top_k,
            use_reranking=request.use_reranking
            if request.use_reranking is not None
            else self.enable_reranking,
        )
        if not sources:
            sources = self._fallback_sources(request.question, request.filters, request.top_k or 5)
        if not sources:
            latency_ms = int((time.perf_counter() - start) * 1000)
            answer = "Je ne sais pas sur la base des documents disponibles."
            self.history_repository.create_entry(
                question=request.question,
                answer=answer,
                sources_json=[],
                filters_json=request.filters.model_dump(),
                latency_ms=latency_ms,
            )
            return QueryResponse(
                answer=answer,
                sources=[],
                used_context_count=0,
                latency_ms=latency_ms,
                status="not_found",
                answer_format=request.answer_format,
            )
        prompt = build_query_prompt(request.question, sources, request.answer_format)
        raw_answer = self.llm_provider.generate(prompt)
        display_sources = self._select_display_sources(raw_answer, sources)
        answer = format_citations(raw_answer, display_sources)
        latency_ms = int((time.perf_counter() - start) * 1000)
        self.history_repository.create_entry(
            question=request.question,
            answer=answer,
            sources_json=[source.model_dump() for source in display_sources],
            filters_json=request.filters.model_dump(),
            latency_ms=latency_ms,
        )
        return QueryResponse(
            answer=answer,
            sources=display_sources,
            used_context_count=len(display_sources),
            latency_ms=latency_ms,
            status="answered",
            answer_format=request.answer_format,
        )

    def summarize_document(self, document_id: str) -> DocumentSummaryResponse:
        start = time.perf_counter()
        document = self.documents_repository.get_document(document_id)
        chunks = self.documents_repository.list_chunks_for_document(document_id)[: self.max_summary_chunks]
        sources = [
            SourceSnippet(
                document_id=document_id,
                document_name=document.original_filename,
                chunk_id=chunk.id,
                excerpt=chunk.text,
                page_number=chunk.page_number,
                section_title=chunk.section_title,
                score=None,
            )
            for chunk in chunks
        ]
        prompt = build_summary_prompt(document.original_filename, sources)
        raw_summary = self.llm_provider.generate(prompt)
        display_sources = self._select_display_sources(raw_summary, sources)
        summary = format_citations(raw_summary, display_sources)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return DocumentSummaryResponse(
            document_id=document_id,
            summary=summary,
            sources=display_sources,
            latency_ms=latency_ms,
        )

    def compare_documents(self, request: CompareDocumentsRequest) -> QueryResponse:
        left_document = self.documents_repository.get_document(request.left_document_id)
        right_document = self.documents_repository.get_document(request.right_document_id)
        compare_request = QueryRequest(
            question=(
                f"{request.question}\n"
                f"Compare the documents '{left_document.original_filename}' and '{right_document.original_filename}'. "
                "Highlight agreements, differences, and missing information."
            ),
            filters=QueryFilters(
                document_ids=[request.left_document_id, request.right_document_id],
                tags=[],
            ),
            answer_format=request.answer_format,
            use_reranking=True,
            top_k=8,
        )
        return self.answer_query(compare_request)

    def _fallback_sources(
        self,
        question: str,
        filters: QueryFilters,
        top_k: int,
    ) -> list[SourceSnippet]:
        question_tokens = set(self._tokenize(question))
        if not question_tokens:
            return []

        chunks = self.documents_repository.list_all_chunks()
        scored_chunks: list[tuple[int, SourceSnippet]] = []
        for chunk in chunks:
            document = self.documents_repository.get_document(chunk.document_id)
            if filters.document_ids and document.id not in filters.document_ids:
                continue
            if filters.tags and not any(tag in document.tags for tag in filters.tags):
                continue

            chunk_tokens = set(self._tokenize(chunk.text))
            overlap = len(question_tokens & chunk_tokens)
            if overlap == 0:
                continue
            scored_chunks.append(
                (
                    overlap,
                    SourceSnippet(
                        document_id=document.id,
                        document_name=document.original_filename,
                        chunk_id=chunk.id,
                        excerpt=chunk.text,
                        page_number=chunk.page_number,
                        section_title=chunk.section_title,
                        score=float(overlap),
                    ),
                )
            )

        scored_chunks.sort(key=lambda item: item[0], reverse=True)
        return [source for _, source in scored_chunks[:top_k]]

    def _tokenize(self, text: str) -> list[str]:
        return [
            token
            for token in re.findall(r"[a-zA-Z]{3,}", text.lower())
            if token not in self.FALLBACK_STOPWORDS
        ]

    def _select_display_sources(
        self,
        answer: str,
        sources: list[SourceSnippet],
        max_sources: int = 3,
    ) -> list[SourceSnippet]:
        if not sources:
            return []

        answer_tokens = set(self._tokenize(answer))
        if not answer_tokens:
            return sources[:1]

        scored: list[tuple[int, SourceSnippet]] = []
        for source in sources:
            source_tokens = set(self._tokenize(source.excerpt))
            overlap = len(answer_tokens & source_tokens)
            scored.append((overlap, source))

        scored.sort(key=lambda item: ((item[0] > 0), item[0], item[1].score or 0), reverse=True)
        selected = [source for overlap, source in scored if overlap > 0][:max_sources]
        if selected:
            return selected
        return sources[:1]
