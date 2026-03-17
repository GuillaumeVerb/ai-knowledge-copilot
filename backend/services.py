from __future__ import annotations

import logging
import re
import time
from collections import defaultdict

from backend.llm.answer_formatter import format_citations
from backend.llm.generator import LLMProvider
from backend.llm.prompts import build_compare_prompt, build_query_prompt, build_summary_prompt
from backend.models.answer import DocumentSummaryResponse
from backend.models.query import (
    CompareDocumentsRequest,
    QueryFilters,
    QueryRequest,
    QueryResponse,
    SourceSnippet,
    StructuredBlock,
)
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
        sources = self._narrow_sources_for_query(
            request.question,
            sources,
            request.answer_format,
            max_sources=2 if request.answer_format == "default" else 3,
        )
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
                sections=[
                    StructuredBlock(
                        title="No answer found",
                        kind="warning",
                        content="The requested information is not available in the current document set.",
                    )
                ],
            )
        prompt = build_query_prompt(request.question, sources, request.answer_format)
        raw_answer = self.llm_provider.generate(prompt)
        display_sources = self._select_display_sources(raw_answer, sources)
        answer = format_citations(raw_answer, display_sources)
        sections = self._build_answer_sections(
            request.question,
            request.answer_format,
            raw_answer,
            display_sources,
        )
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
            sections=sections,
            comparison_mode=False,
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
        sources = sources[:4]
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
            sections=self._build_summary_sections(raw_summary, display_sources),
        )

    def compare_documents(self, request: CompareDocumentsRequest) -> QueryResponse:
        left_document = self.documents_repository.get_document(request.left_document_id)
        right_document = self.documents_repository.get_document(request.right_document_id)
        start = time.perf_counter()
        left_sources = self.retrieval_service.retrieve(
            request.question,
            filters=QueryFilters(document_ids=[request.left_document_id], tags=[]),
            top_k=2,
            use_reranking=True,
        )
        right_sources = self.retrieval_service.retrieve(
            request.question,
            filters=QueryFilters(document_ids=[request.right_document_id], tags=[]),
            top_k=2,
            use_reranking=True,
        )
        sources = self._narrow_sources_for_query(
            request.question,
            left_sources + right_sources,
            request.answer_format,
            max_sources=4,
        )
        if not sources:
            sources = self._fallback_sources(
                request.question,
                QueryFilters(document_ids=[request.left_document_id, request.right_document_id], tags=[]),
                4,
            )
        prompt = build_compare_prompt(
            request.question,
            left_document.original_filename,
            right_document.original_filename,
            sources,
        )
        raw_answer = self.llm_provider.generate(prompt)
        display_sources = self._select_display_sources(raw_answer, sources, max_sources=4)
        answer = format_citations(raw_answer, display_sources)
        sections = self._build_comparison_sections(
            left_document.original_filename,
            right_document.original_filename,
            display_sources,
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
        self.history_repository.create_entry(
            question=request.question,
            answer=answer,
            sources_json=[source.model_dump() for source in display_sources],
            filters_json={"document_ids": [request.left_document_id, request.right_document_id], "tags": []},
            latency_ms=latency_ms,
        )
        return QueryResponse(
            answer=answer,
            sources=display_sources,
            used_context_count=len(display_sources),
            latency_ms=latency_ms,
            status="answered" if display_sources else "not_found",
            answer_format=request.answer_format,
            sections=sections,
            comparison_mode=True,
        )

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

    def _narrow_sources_for_query(
        self,
        question: str,
        sources: list[SourceSnippet],
        answer_format: str,
        max_sources: int,
    ) -> list[SourceSnippet]:
        if not sources:
            return []
        question_tokens = set(self._tokenize(question))
        narrowed: list[tuple[int, float, SourceSnippet]] = []
        for source in sources:
            excerpt_tokens = set(self._tokenize(source.excerpt))
            overlap = len(question_tokens & excerpt_tokens)
            if overlap == 0 and answer_format == "default":
                continue
            narrowed.append((overlap, source.score or 0.0, source))
        narrowed.sort(key=lambda item: (item[0], item[1]), reverse=True)
        selected = [source for overlap, _, source in narrowed if overlap > 0][:max_sources]
        if selected:
            return selected
        return sources[:max_sources]

    def _build_answer_sections(
        self,
        question: str,
        answer_format: str,
        answer: str,
        sources: list[SourceSnippet],
    ) -> list[StructuredBlock]:
        clean_answer = self._strip_sources_line(answer)
        if answer_format == "resume":
            return [
                StructuredBlock(title="Summary", kind="bullets", items=self._extract_bullets(clean_answer, fallback_limit=4))
            ]
        if answer_format == "etapes":
            return [
                StructuredBlock(title="Steps", kind="numbered", items=self._extract_bullets(clean_answer, fallback_limit=4))
            ]
        if answer_format == "risques":
            return [
                StructuredBlock(title="Risks", kind="warning", items=self._extract_bullets(clean_answer, fallback_limit=4))
            ]
        if answer_format == "faq":
            return [
                StructuredBlock(title="FAQ", kind="faq", content=f"Q: {question}\nA: {clean_answer}")
            ]
        return [
            StructuredBlock(title="Summary", kind="summary", content=clean_answer),
            StructuredBlock(
                title="Sources used",
                kind="bullets",
                items=[f"{source.document_name}" + (f" p.{source.page_number}" if source.page_number else "") for source in sources],
            ),
        ]

    def _build_summary_sections(
        self,
        summary: str,
        sources: list[SourceSnippet],
    ) -> list[StructuredBlock]:
        clean_summary = self._strip_sources_line(summary)
        bullets = self._extract_bullets(clean_summary, fallback_limit=4)
        overview = bullets[0] if bullets else clean_summary
        extra_points = bullets[1:] if len(bullets) > 1 else bullets[:1]
        return [
            StructuredBlock(title="Overview", kind="summary", content=overview),
            StructuredBlock(title="Key points", kind="bullets", items=extra_points),
            StructuredBlock(
                title="Sources",
                kind="bullets",
                items=[f"{source.document_name}" + (f" p.{source.page_number}" if source.page_number else "") for source in sources],
            ),
        ]

    def _build_comparison_sections(
        self,
        left_name: str,
        right_name: str,
        sources: list[SourceSnippet],
    ) -> list[StructuredBlock]:
        by_document: dict[str, list[str]] = defaultdict(list)
        for source in sources:
            by_document[source.document_name].extend(self._split_sentences(source.excerpt))

        left_points = self._dedupe_preserve_order(by_document.get(left_name, []))[:2]
        right_points = self._dedupe_preserve_order(by_document.get(right_name, []))[:2]
        left_terms = set(self._tokenize(" ".join(by_document.get(left_name, []))))
        right_terms = set(self._tokenize(" ".join(by_document.get(right_name, []))))
        similarities = sorted(left_terms & right_terms)[:3]

        return [
            StructuredBlock(
                title="Summary",
                kind="comparison",
                content=f"{left_name} and {right_name} cover related procedures but emphasize different operational details.",
            ),
            StructuredBlock(
                title="Points communs",
                kind="bullets",
                items=[f"Both documents mention {', '.join(similarities)}."] if similarities else ["Both documents address the same operational theme."],
            ),
            StructuredBlock(
                title="Différences",
                kind="bullets",
                items=[f"{left_name}: {point}" for point in left_points] + [f"{right_name}: {point}" for point in right_points],
            ),
            StructuredBlock(
                title="Impact opérationnel",
                kind="warning",
                items=["Align escalation expectations across teams and clarify who owns each step."],
            ),
        ]

    def _extract_bullets(self, text: str, fallback_limit: int = 4) -> list[str]:
        explicit = [line.strip("- ").strip() for line in text.splitlines() if line.strip().startswith("-")]
        if explicit:
            return explicit[:fallback_limit]
        return self._split_sentences(text)[:fallback_limit]

    def _strip_sources_line(self, text: str) -> str:
        return re.sub(r"\n\s*Sources:\s.*$", "", text, flags=re.S).strip()

    def _split_sentences(self, text: str) -> list[str]:
        return [part.strip(" -") for part in re.split(r"(?<=[.!?])\s+|\n+", text) if part.strip()]

    def _dedupe_preserve_order(self, values: list[str]) -> list[str]:
        seen = set()
        result = []
        for value in values:
            normalized = value.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            result.append(value)
        return result
