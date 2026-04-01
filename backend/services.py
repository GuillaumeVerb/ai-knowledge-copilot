from __future__ import annotations

import logging
import re
import time
from collections import defaultdict
from itertools import combinations

from backend.llm.answer_formatter import format_citations
from backend.llm.generator import LLMProvider, StubLLMProvider
from backend.llm.prompts import build_compare_prompt, build_query_prompt, build_summary_prompt
from backend.models.assistant import AssistantProfileRead
from backend.models.answer import DocumentSummaryResponse
from backend.models.query import (
    CompareDocumentsRequest,
    QueryFilters,
    QueryRequest,
    QueryResponse,
    SynthesizeDocumentsRequest,
    SourceSnippet,
    StructuredBlock,
)
from backend.repositories.assistants_repo import AssistantProfilesRepository
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
        assistants_repository: AssistantProfilesRepository,
        enable_reranking: bool,
        max_summary_chunks: int,
    ):
        self.retrieval_service = retrieval_service
        self.llm_provider = llm_provider
        self.history_repository = history_repository
        self.documents_repository = documents_repository
        self.assistants_repository = assistants_repository
        self.enable_reranking = enable_reranking
        self.max_summary_chunks = max_summary_chunks
        self.fallback_llm_provider = StubLLMProvider()

    def answer_query(self, request: QueryRequest) -> QueryResponse:
        start = time.perf_counter()
        assistant = self._resolve_assistant(request.assistant_id)
        effective_filters, assistant_scope_empty = self._resolve_filters(request.filters, assistant)
        normalized_format = self._resolve_answer_format(request.answer_format, assistant)
        language = self._resolve_request_language(request, assistant)
        top_k = request.top_k or (assistant.retrieval_top_k if assistant else None)
        use_reranking = (
            request.use_reranking
            if request.use_reranking is not None
            else (assistant.use_reranking if assistant else self.enable_reranking)
        )
        clarification_needed, clarifying_question = self._detect_ambiguity(request.question, effective_filters, language)
        sources: list[SourceSnippet] = []
        if not assistant_scope_empty:
            sources = self.retrieval_service.retrieve(
                request.question,
                filters=effective_filters,
                top_k=top_k,
                use_reranking=use_reranking,
            )
        if not sources and not assistant_scope_empty:
            sources = self._fallback_sources(request.question, effective_filters, top_k or 5)
        sources = self._narrow_sources_for_query(
            request.question,
            sources,
            normalized_format,
            max_sources=2 if normalized_format in {"default", "concise"} else 3,
        )
        if not sources:
            latency_ms = int((time.perf_counter() - start) * 1000)
            answer = self._unknown_answer(language)
            suggestions = self._build_suggestions(
                request.question,
                request.filters,
                [],
                clarification_needed=clarification_needed,
            )
            history_entry = self.history_repository.create_entry(
                question=request.question,
                answer=answer,
                sources_json=[],
                filters_json=self._history_filters_payload(effective_filters, assistant),
                latency_ms=latency_ms,
            )
            return QueryResponse(
                answer=answer,
                sources=[],
                confidence="Low",
                safety="None",
                suggestions=suggestions,
                detected_language=language,
                used_context_count=0,
                latency_ms=latency_ms,
                status="not_found",
                answer_format=normalized_format,
                sections=[
                    StructuredBlock(
                        title="No answer found",
                        kind="warning",
                        content=self._no_answer_explanation(language),
                    )
                ],
                clarification_needed=clarification_needed,
                clarifying_question=clarifying_question,
                confidence_label="low",
                confidence_score=0.0,
                confidence_reason=self._translate_confidence_reason(
                    self._no_evidence_reason(assistant_scope_empty),
                    language,
                ),
                evidence_documents=[],
                evidence_summary="0 source excerpts across 0 documents.",
                caution=self._no_evidence_caution(assistant_scope_empty),
                history_id=history_entry.id,
                assistant_id=assistant.id if assistant else None,
                assistant_name=assistant.name if assistant else None,
            )
        prompt = build_query_prompt(
            request.question,
            sources,
            normalized_format,
            language=language,
            conversation_history=request.conversation_history,
            assistant_name=assistant.name if assistant else None,
            assistant_instructions=assistant.instructions if assistant else None,
            assistant_tone=assistant.tone if assistant else None,
        )
        raw_answer = self._generate_answer(prompt)
        display_sources = self._select_display_sources(raw_answer, sources)
        answer = format_citations(raw_answer, display_sources)
        sections = self._build_answer_sections(
            request.question,
            normalized_format,
            raw_answer,
            display_sources,
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
        confidence_score, confidence_label, confidence_reason = self._compute_confidence(
            request.question,
            display_sources,
            comparison_mode=False,
        )
        suggestions = self._build_suggestions(
            request.question,
            effective_filters,
            display_sources,
            clarification_needed=clarification_needed,
        )
        history_entry = self.history_repository.create_entry(
            question=request.question,
            answer=answer,
            sources_json=[source.model_dump() for source in display_sources],
            filters_json=self._history_filters_payload(effective_filters, assistant),
            latency_ms=latency_ms,
        )
        return QueryResponse(
            answer=answer,
            sources=display_sources,
            confidence=self._display_confidence(confidence_label),
            safety=self._safety_label(display_sources, confidence_label),
            suggestions=suggestions,
            detected_language=language,
            used_context_count=len(display_sources),
            latency_ms=latency_ms,
            status="answered",
            answer_format=normalized_format,
            sections=sections,
            comparison_mode=False,
            clarification_needed=clarification_needed,
            clarifying_question=clarifying_question,
            confidence_label=confidence_label,
            confidence_score=confidence_score,
            confidence_reason=confidence_reason,
            evidence_documents=self._evidence_documents(display_sources),
            evidence_summary=self._build_evidence_summary(display_sources),
            caution=self._build_caution(confidence_label, display_sources),
            history_id=history_entry.id,
            assistant_id=assistant.id if assistant else None,
            assistant_name=assistant.name if assistant else None,
        )

    def summarize_document(self, document_id: str) -> DocumentSummaryResponse:
        start = time.perf_counter()
        language = "fr"
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
        prompt = build_summary_prompt(document.original_filename, sources, language=language)
        raw_summary = self._generate_answer(prompt)
        display_sources = self._select_display_sources(raw_summary, sources)
        summary = format_citations(raw_summary, display_sources)
        latency_ms = int((time.perf_counter() - start) * 1000)
        return DocumentSummaryResponse(
            document_id=document_id,
            summary=summary,
            sources=display_sources,
            latency_ms=latency_ms,
            sections=self._build_summary_sections(raw_summary, display_sources),
            evidence_documents=self._evidence_documents(display_sources),
            evidence_summary=self._build_evidence_summary(display_sources),
        )

    def compare_documents(self, request: CompareDocumentsRequest) -> QueryResponse:
        left_document = self.documents_repository.get_document(request.left_document_id)
        right_document = self.documents_repository.get_document(request.right_document_id)
        start = time.perf_counter()
        normalized_format = self._normalize_answer_format(request.answer_format)
        language = self._resolve_language(request.language, request.question)
        clarification_needed, clarifying_question = self._detect_ambiguity(
            request.question,
            QueryFilters(document_ids=[request.left_document_id, request.right_document_id]),
            language,
        )
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
            normalized_format,
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
            language=language,
        )
        raw_answer = self._generate_answer(prompt)
        display_sources = self._select_display_sources(raw_answer, sources, max_sources=4)
        answer = format_citations(raw_answer, display_sources)
        sections = self._build_comparison_sections(
            left_document.original_filename,
            right_document.original_filename,
            display_sources,
        )
        latency_ms = int((time.perf_counter() - start) * 1000)
        confidence_score, confidence_label, confidence_reason = self._compute_confidence(
            request.question,
            display_sources,
            comparison_mode=True,
        )
        suggestions = self._build_suggestions(
            request.question,
            QueryFilters(document_ids=[request.left_document_id, request.right_document_id]),
            display_sources,
            clarification_needed=clarification_needed,
            comparison_mode=True,
        )
        history_entry = self.history_repository.create_entry(
            question=request.question,
            answer=answer,
            sources_json=[source.model_dump() for source in display_sources],
            filters_json={"document_ids": [request.left_document_id, request.right_document_id], "tags": []},
            latency_ms=latency_ms,
        )
        return QueryResponse(
            answer=answer,
            sources=display_sources,
            confidence=self._display_confidence(confidence_label),
            safety=self._safety_label(display_sources, confidence_label),
            suggestions=suggestions,
            detected_language=language,
            used_context_count=len(display_sources),
            latency_ms=latency_ms,
            status="answered" if display_sources else "not_found",
            answer_format=normalized_format,
            sections=sections,
            comparison_mode=True,
            clarification_needed=clarification_needed,
            clarifying_question=clarifying_question,
            confidence_label=confidence_label,
            confidence_score=confidence_score,
            confidence_reason=confidence_reason,
            evidence_documents=self._evidence_documents(display_sources),
            evidence_summary=self._build_evidence_summary(display_sources),
            caution=self._build_caution(confidence_label, display_sources, comparison_mode=True),
            history_id=history_entry.id,
        )

    def synthesize_documents(self, request: SynthesizeDocumentsRequest) -> QueryResponse:
        start = time.perf_counter()
        normalized_format = self._normalize_answer_format(request.answer_format)
        language = self._resolve_language(request.language, request.question)
        clarification_needed, clarifying_question = self._detect_ambiguity(
            request.question,
            QueryFilters(document_ids=request.document_ids),
            language,
        )
        documents = [self.documents_repository.get_document(document_id) for document_id in request.document_ids]
        filters = QueryFilters(document_ids=request.document_ids)
        sources = self.retrieval_service.retrieve(
            request.question,
            filters=filters,
            top_k=6,
            use_reranking=True,
        )
        sources = self._narrow_sources_for_query(
            request.question,
            sources,
            normalized_format,
            max_sources=4,
        )
        if not sources:
            sources = self._fallback_sources(request.question, filters, 4)
        if not sources:
            latency_ms = int((time.perf_counter() - start) * 1000)
            answer = self._unknown_answer(language)
            suggestions = self._build_suggestions(
                request.question,
                QueryFilters(document_ids=request.document_ids),
                [],
                clarification_needed=clarification_needed,
                synthesis_mode=True,
            )
            history_entry = self.history_repository.create_entry(
                question=request.question,
                answer=answer,
                sources_json=[],
                filters_json={"document_ids": request.document_ids, "mode": "synthesis"},
                latency_ms=latency_ms,
            )
            return QueryResponse(
                answer=answer,
                sources=[],
                confidence="Low",
                safety="None",
                suggestions=suggestions,
                detected_language=language,
                used_context_count=0,
                latency_ms=latency_ms,
                status="not_found",
                answer_format=normalized_format,
                sections=[
                    StructuredBlock(
                        title="No synthesis available",
                        kind="warning",
                        content=self._no_synthesis_explanation(language),
                    )
                ],
                clarification_needed=clarification_needed,
                clarifying_question=clarifying_question,
                confidence_label="low",
                confidence_score=0.0,
                confidence_reason=self._translate_confidence_reason(
                    "The selected documents do not contain enough relevant overlap for a grounded synthesis.",
                    language,
                ),
                evidence_documents=[],
                evidence_summary="0 source excerpts across 0 documents.",
                caution="The selected documents do not provide enough overlapping evidence for a reliable synthesis.",
                history_id=history_entry.id,
            )

        prompt = build_query_prompt(
            request.question,
            sources,
            normalized_format,
            language=language,
            conversation_history=request.conversation_history,
        )
        raw_answer = self._generate_answer(prompt)
        display_sources = self._select_display_sources(raw_answer, sources, max_sources=4)
        answer = format_citations(raw_answer, display_sources)
        latency_ms = int((time.perf_counter() - start) * 1000)
        confidence_score, confidence_label, confidence_reason = self._compute_confidence(
            request.question,
            display_sources,
            comparison_mode=True,
        )
        suggestions = self._build_suggestions(
            request.question,
            QueryFilters(document_ids=request.document_ids),
            display_sources,
            clarification_needed=clarification_needed,
            synthesis_mode=True,
        )
        history_entry = self.history_repository.create_entry(
            question=request.question,
            answer=answer,
            sources_json=[source.model_dump() for source in display_sources],
            filters_json={"document_ids": request.document_ids, "mode": "synthesis"},
            latency_ms=latency_ms,
        )
        return QueryResponse(
            answer=answer,
            sources=display_sources,
            confidence=self._display_confidence(confidence_label),
            safety=self._safety_label(display_sources, confidence_label),
            suggestions=suggestions,
            detected_language=language,
            used_context_count=len(display_sources),
            latency_ms=latency_ms,
            status="answered",
            answer_format=normalized_format,
            sections=self._build_synthesis_sections(documents, raw_answer, display_sources),
            comparison_mode=False,
            clarification_needed=clarification_needed,
            clarifying_question=clarifying_question,
            confidence_label=confidence_label,
            confidence_score=confidence_score,
            confidence_reason=confidence_reason,
            evidence_documents=self._evidence_documents(display_sources),
            evidence_summary=self._build_evidence_summary(display_sources),
            caution=self._build_caution(confidence_label, display_sources, synthesis_mode=True),
            history_id=history_entry.id,
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

    def _generate_answer(self, prompt: str) -> str:
        try:
            return self.llm_provider.generate(prompt)
        except Exception as exc:
            logger.warning("Primary LLM provider failed, using stub fallback: %s", exc)
            return self.fallback_llm_provider.generate(prompt)

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
            if overlap == 0 and answer_format in {"default", "concise"}:
                continue
            narrowed.append((overlap, source.score or 0.0, source))
        narrowed.sort(key=lambda item: (item[0], item[1]), reverse=True)
        selected = [source for overlap, _, source in narrowed if overlap > 0][:max_sources]
        if selected:
            return selected
        return sources[:max_sources]

    def _resolve_assistant(self, assistant_id: str | None) -> AssistantProfileRead | None:
        if assistant_id:
            return self.assistants_repository.get_profile(assistant_id)
        return self.assistants_repository.get_default_profile()

    def _resolve_filters(
        self,
        request_filters: QueryFilters,
        assistant: AssistantProfileRead | None,
    ) -> tuple[QueryFilters, bool]:
        if assistant is None:
            return request_filters, False

        assistant_scope_active = bool(
            assistant.document_ids or assistant.tags or assistant.categories or assistant.latest_only
        )
        allowed_documents = self.documents_repository.list_documents(
            include_superseded=not assistant.latest_only
        )
        if assistant.document_ids:
            allowed_documents = [
                document for document in allowed_documents if document.id in assistant.document_ids
            ]
        if assistant.tags:
            allowed_documents = [
                document for document in allowed_documents
                if any(tag in document.tags for tag in assistant.tags)
            ]
        if assistant.categories:
            allowed_documents = [
                document for document in allowed_documents
                if document.category in assistant.categories
            ]
        allowed_ids = [document.id for document in allowed_documents]
        if request_filters.document_ids:
            if assistant_scope_active:
                allowed_ids = [document_id for document_id in request_filters.document_ids if document_id in set(allowed_ids)]
            else:
                allowed_ids = request_filters.document_ids
        effective_filters = request_filters.model_copy(
            update={
                "document_ids": allowed_ids if (assistant_scope_active or request_filters.document_ids) else request_filters.document_ids,
            }
        )
        return effective_filters, assistant_scope_active and not allowed_ids

    def _resolve_answer_format(
        self,
        requested_format: str,
        assistant: AssistantProfileRead | None,
    ) -> str:
        if requested_format != "default":
            return self._normalize_answer_format(requested_format)
        if assistant:
            return self._normalize_answer_format(assistant.answer_format)
        return self._normalize_answer_format(requested_format)

    def _resolve_request_language(
        self,
        request: QueryRequest,
        assistant: AssistantProfileRead | None,
    ) -> str:
        requested_language = request.language
        if requested_language == "auto" and assistant and assistant.language != "auto":
            requested_language = assistant.language
        return self._resolve_language(requested_language, request.question)

    def _history_filters_payload(
        self,
        filters: QueryFilters,
        assistant: AssistantProfileRead | None,
    ) -> dict:
        payload = filters.model_dump()
        if assistant:
            payload["assistant_id"] = assistant.id
            payload["assistant_name"] = assistant.name
        return payload

    def _no_evidence_reason(self, assistant_scope_empty: bool) -> str:
        if assistant_scope_empty:
            return "The assistant scope does not include any indexed documents for this request."
        return "No sufficiently relevant evidence found in the indexed documents."

    def _no_evidence_caution(self, assistant_scope_empty: bool) -> str:
        if assistant_scope_empty:
            return "The current assistant configuration does not match any indexed documents. Broaden the assistant scope or upload matching files."
        return "The assistant did not find enough grounded evidence to answer safely."

    def _build_answer_sections(
        self,
        question: str,
        answer_format: str,
        answer: str,
        sources: list[SourceSnippet],
    ) -> list[StructuredBlock]:
        clean_answer = self._strip_sources_line(answer)
        if answer_format in {"resume", "summary"}:
            return [
                StructuredBlock(title="Summary", kind="bullets", items=self._extract_bullets(clean_answer, fallback_limit=4))
            ]
        if answer_format in {"etapes", "checklist"}:
            return [
                StructuredBlock(title="Checklist", kind="numbered", items=self._extract_bullets(clean_answer, fallback_limit=5))
            ]
        if answer_format == "risques":
            return [
                StructuredBlock(title="Risks", kind="warning", items=self._extract_bullets(clean_answer, fallback_limit=4))
            ]
        if answer_format == "faq":
            return [
                StructuredBlock(title="FAQ", kind="faq", content=f"Q: {question}\nA: {clean_answer}")
            ]
        if answer_format == "detailed":
            bullets = self._extract_bullets(clean_answer, fallback_limit=5)
            return [
                StructuredBlock(title="Executive answer", kind="summary", content=bullets[0] if bullets else clean_answer),
                StructuredBlock(title="Key details", kind="bullets", items=bullets[1:] if len(bullets) > 1 else bullets),
                StructuredBlock(
                    title="Source coverage",
                    kind="bullets",
                    items=[f"{source.document_name}" + (f" p.{source.page_number}" if source.page_number else "") for source in sources],
                ),
            ]
        if answer_format == "comparison":
            points = self._extract_bullets(clean_answer, fallback_limit=6)
            midpoint = max(1, len(points) // 2)
            return [
                StructuredBlock(title="Comparison summary", kind="summary", content=clean_answer),
                StructuredBlock(title="Differences", kind="bullets", items=points[:midpoint]),
                StructuredBlock(title="Operational impact", kind="bullets", items=points[midpoint:] or points[:2]),
            ]
        if answer_format == "structured":
            bullets = self._extract_bullets(clean_answer, fallback_limit=5)
            return [
                StructuredBlock(title="Answer", kind="summary", content=bullets[0] if bullets else clean_answer),
                StructuredBlock(title="Supporting points", kind="bullets", items=bullets[1:] if len(bullets) > 1 else bullets),
                StructuredBlock(
                    title="Sources used",
                    kind="bullets",
                    items=[f"{source.document_name}" + (f" p.{source.page_number}" if source.page_number else "") for source in sources],
                ),
            ]
        return [
            StructuredBlock(title="Summary", kind="summary", content=clean_answer),
            StructuredBlock(
                title="Sources used",
                kind="bullets",
                items=[f"{source.document_name}" + (f" p.{source.page_number}" if source.page_number else "") for source in sources],
            ),
        ]

    def _normalize_answer_format(self, answer_format: str) -> str:
        aliases = {
            "default": "concise",
            "resume": "summary",
            "etapes": "checklist",
        }
        return aliases.get(answer_format, answer_format)

    def _compute_confidence(
        self,
        question: str,
        sources: list[SourceSnippet],
        *,
        comparison_mode: bool,
    ) -> tuple[float, str, str]:
        if not sources:
            return 0.0, "low", "No sufficiently relevant evidence found in the indexed documents."

        top_score = max((source.score or 0.0) for source in sources)
        avg_score = sum((source.score or 0.0) for source in sources) / len(sources)
        support_score = min(len(sources) / 3.0, 1.0)
        similarity_score = min(max((top_score + avg_score) / 2.0, 0.0), 1.0)
        consistency_score = self._consistency_score(question, sources, comparison_mode=comparison_mode)
        confidence_score = max(
            0.0,
            min(1.0, 0.3 * support_score + 0.45 * similarity_score + 0.25 * consistency_score),
        )
        if confidence_score >= 0.75:
            return confidence_score, "high", (
                f"High support from {len(sources)} chunk(s), strong retrieval similarity, "
                f"and consistent evidence across the cited context."
            )
        if confidence_score >= 0.45:
            return confidence_score, "medium", (
                f"Supported by {len(sources)} chunk(s), but either retrieval similarity or agreement "
                f"between chunks is only moderate."
            )
        return confidence_score, "low", (
            f"Evidence is limited: {len(sources)} supporting chunk(s) with weak similarity or low consistency."
        )

    def _consistency_score(
        self,
        question: str,
        sources: list[SourceSnippet],
        *,
        comparison_mode: bool,
    ) -> float:
        if len(sources) == 1:
            return 0.7

        question_tokens = set(self._tokenize(question))
        pair_scores: list[float] = []
        for left, right in combinations(sources, 2):
            left_tokens = set(self._tokenize(left.excerpt))
            right_tokens = set(self._tokenize(right.excerpt))
            shared = left_tokens & right_tokens
            total = left_tokens | right_tokens
            pair_scores.append((len(shared) / len(total)) if total else 0.0)

        base_score = sum(pair_scores) / len(pair_scores) if pair_scores else 0.0
        question_coverage = sum(
            1.0
            for source in sources
            if question_tokens and question_tokens & set(self._tokenize(source.excerpt))
        ) / len(sources)
        if comparison_mode and len({source.document_id for source in sources}) > 1:
            return min(1.0, 0.55 * question_coverage + 0.45 * base_score)
        return min(1.0, 0.4 * question_coverage + 0.6 * base_score)

    def _evidence_documents(self, sources: list[SourceSnippet]) -> list[str]:
        return list(dict.fromkeys(source.document_name for source in sources))

    def _build_evidence_summary(self, sources: list[SourceSnippet]) -> str:
        document_count = len(self._evidence_documents(sources))
        return f"{len(sources)} source excerpt(s) across {document_count} document(s)."

    def _build_caution(
        self,
        confidence_label: str,
        sources: list[SourceSnippet],
        *,
        comparison_mode: bool = False,
        synthesis_mode: bool = False,
    ) -> str:
        if not sources:
            return "No grounded evidence was returned."
        if confidence_label == "high":
            return ""
        if synthesis_mode:
            return "Treat this synthesis as directional. Review the cited evidence before turning it into guidance."
        if comparison_mode:
            return "This comparison blends evidence from multiple documents. Check the source excerpts before aligning teams on differences."
        if confidence_label == "medium":
            return "Evidence is useful but not fully concentrated. Validate the cited excerpts before acting on the answer."
        return "Evidence is limited or dispersed. Use the cited excerpts to confirm the answer before relying on it."

    def _safety_label(self, sources: list[SourceSnippet], confidence_label: str) -> str:
        if not sources:
            return "None"
        if confidence_label == "high":
            return "Grounded"
        return "Limited"

    def _display_confidence(self, confidence_label: str) -> str:
        return confidence_label.capitalize()

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
                title="Shared themes",
                kind="bullets",
                items=[f"Both documents mention {', '.join(similarities)}."] if similarities else ["Both documents address the same operational theme."],
            ),
            StructuredBlock(
                title="Structured differences",
                kind="bullets",
                items=[f"{left_name}: {point}" for point in left_points] + [f"{right_name}: {point}" for point in right_points],
            ),
            StructuredBlock(
                title="Key operational changes",
                kind="warning",
                items=["Align escalation expectations across teams and clarify who owns each step."],
            ),
            StructuredBlock(
                title="Contradictions",
                kind="bullets",
                items=self._detect_contradictions(left_points, right_points),
            ),
        ]

    def _build_synthesis_sections(
        self,
        documents,
        answer: str,
        sources: list[SourceSnippet],
    ) -> list[StructuredBlock]:
        grouped: dict[str, list[str]] = defaultdict(list)
        for source in sources:
            grouped[source.document_name].append(self._trim_excerpt(source.excerpt))
        return [
            StructuredBlock(
                title="Overview",
                kind="summary",
                content=self._strip_sources_line(answer),
            ),
            StructuredBlock(
                title="Key themes",
                kind="bullets",
                items=self._extract_themes(sources),
            ),
            StructuredBlock(
                title="Documents synthesized",
                kind="bullets",
                items=[document.original_filename for document in documents],
            ),
            StructuredBlock(
                title="Grouped insights",
                kind="bullets",
                items=self._extract_bullets(self._strip_sources_line(answer), fallback_limit=4),
            ),
            StructuredBlock(
                title="Source highlights",
                kind="bullets",
                items=self._extract_document_specific_points(grouped),
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

    def _extract_document_specific_points(self, grouped: dict[str, list[str]]) -> list[str]:
        items: list[str] = []
        for document_name, excerpts in grouped.items():
            for excerpt in self._dedupe_preserve_order(excerpts)[:2]:
                items.append(f"{document_name}: {excerpt}")
        return items[:4]

    def _trim_excerpt(self, text: str) -> str:
        sentences = self._split_sentences(text)
        return sentences[0] if sentences else text.strip()

    def _detect_ambiguity(
        self,
        question: str,
        filters: QueryFilters,
        language: str,
    ) -> tuple[bool, Optional[str]]:
        lowered = question.strip().lower()
        tokens = self._tokenize(question)
        ambiguous_phrases = {"this", "that", "it", "they", "them", "these", "those", "latest version"}
        if len(tokens) < 4 or any(phrase in lowered for phrase in ambiguous_phrases):
            if not filters.document_ids and not filters.tags and not filters.categories:
                return True, (
                    "Pouvez-vous préciser le périmètre, l’équipe ou la catégorie de documents à utiliser ?"
                    if language == "fr"
                    else "Can you clarify which document set, team, or category I should use?"
                )
        return False, None

    def _build_suggestions(
        self,
        question: str,
        filters: QueryFilters,
        sources: list[SourceSnippet],
        *,
        clarification_needed: bool,
        comparison_mode: bool = False,
        synthesis_mode: bool = False,
    ) -> list[str]:
        suggestions: list[str] = []
        if clarification_needed:
            suggestions.append(
                "Préciser le périmètre ou le corpus ciblé avant de répondre."
                if self._is_french_question(question)
                else "Clarify the scope or target document set before answering."
            )
        if not filters.categories:
            suggestions.append(
                "Souhaitez-vous limiter aux documents RH ?"
                if self._is_french_question(question)
                else "Do you want HR documents only?"
            )
        if not filters.tags:
            suggestions.append(
                "Filtrer par tags pour réduire le périmètre de recherche."
                if self._is_french_question(question)
                else "Filter by tags to narrow the retrieval set."
            )
        if not comparison_mode:
            suggestions.append(
                "Résumer un document pour obtenir une réponse plus ciblée."
                if self._is_french_question(question)
                else "Summarize a single document for a focused answer."
            )
        if not synthesis_mode:
            suggestions.append(
                "Comparer deux documents pour mettre en évidence les différences."
                if self._is_french_question(question)
                else "Compare two documents to highlight policy differences."
            )
        if sources and len({source.document_id for source in sources}) > 1:
            suggestions.append(
                "Synthétiser les documents cités par thème."
                if self._is_french_question(question)
                else "Synthesize the cited documents into grouped insights."
            )
        return list(dict.fromkeys(suggestions))[:4]

    def _detect_contradictions(self, left_points: list[str], right_points: list[str]) -> list[str]:
        contradictions: list[str] = []
        for left_point in left_points:
            for right_point in right_points:
                left_lower = left_point.lower()
                right_lower = right_point.lower()
                if ("require" in left_lower and "not" in right_lower) or ("not" in left_lower and "require" in right_lower):
                    contradictions.append(f"{left_point} | {right_point}")
        if contradictions:
            return contradictions[:2]
        return ["No direct contradiction detected in the top retrieved excerpts."]

    def _extract_themes(self, sources: list[SourceSnippet]) -> list[str]:
        terms: dict[str, int] = defaultdict(int)
        for source in sources:
            for token in self._tokenize(source.excerpt):
                terms[token] += 1
        ranked = [term for term, count in sorted(terms.items(), key=lambda item: (-item[1], item[0])) if count > 1]
        if not ranked:
            return ["No dominant shared theme detected beyond the cited excerpts."]
        return [f"Theme: {term}" for term in ranked[:4]]

    def _resolve_language(self, requested_language: str, question: str) -> str:
        if requested_language in {"fr", "en"}:
            return requested_language
        return "fr" if self._is_french_question(question) else "en"

    def _is_french_question(self, text: str) -> bool:
        lowered = text.lower()
        french_markers = {
            "bonjour", "comment", "pourquoi", "quelle", "quelles", "quels", "est-ce", "documents",
            "procédure", "synthèse", "résumé", "réponse", "politique", "sécurité", "support", "rh",
            "bonjour", "avec", "sans", "entre", "dans", "sur", "des", "les", "une", "le", "la",
        }
        marker_hits = sum(1 for marker in french_markers if marker in lowered)
        accent_hits = sum(1 for char in lowered if char in "éèàùçôîâêûëïü")
        return marker_hits >= 2 or accent_hits >= 1

    def _unknown_answer(self, language: str) -> str:
        return (
            "Je ne sais pas sur la base des documents disponibles."
            if language == "fr"
            else "I don't know based on available documents."
        )

    def _no_answer_explanation(self, language: str) -> str:
        return (
            "Je ne sais pas sur la base des documents disponibles. Les preuves actuelles ne suffisent pas pour répondre de façon fiable."
            if language == "fr"
            else "I don't know based on available documents. The current evidence is not strong enough to answer safely."
        )

    def _no_synthesis_explanation(self, language: str) -> str:
        return (
            "Je ne sais pas sur la base des documents disponibles. Les documents sélectionnés ne contiennent pas assez d’éléments convergents pour une synthèse fiable."
            if language == "fr"
            else "I don't know based on available documents. The selected set does not contain enough shared evidence for a safe synthesis."
        )

    def _translate_confidence_reason(self, reason: str, language: str) -> str:
        if language != "fr":
            return reason
        translations = {
            "No sufficiently relevant evidence found in the indexed documents.": "Aucune preuve suffisamment pertinente n’a été trouvée dans les documents indexés.",
            "The selected documents do not contain enough relevant overlap for a grounded synthesis.": "Les documents sélectionnés ne contiennent pas assez de recoupements pertinents pour produire une synthèse fondée.",
            "The assistant scope does not include any indexed documents for this request.": "Le périmètre de l’assistant ne contient aucun document indexé correspondant à cette demande.",
        }
        return translations.get(reason, reason)
