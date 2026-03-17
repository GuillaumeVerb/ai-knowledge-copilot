from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


AnswerFormat = Literal["default", "resume", "etapes", "risques", "faq"]


class QueryFilters(BaseModel):
    document_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class QueryRequest(BaseModel):
    question: str = Field(min_length=3)
    filters: QueryFilters = Field(default_factory=QueryFilters)
    top_k: Optional[int] = None
    answer_format: AnswerFormat = "default"
    use_reranking: Optional[bool] = None


class SourceSnippet(BaseModel):
    document_id: str
    document_name: str
    chunk_id: str
    excerpt: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    score: Optional[float] = None


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceSnippet]
    used_context_count: int
    latency_ms: int
    status: Literal["answered", "not_found"]
    answer_format: AnswerFormat = "default"


class CompareDocumentsRequest(BaseModel):
    question: str = Field(min_length=3)
    left_document_id: str
    right_document_id: str
    answer_format: Literal["default", "resume", "etapes", "risques"] = "default"


class HistoryItem(BaseModel):
    id: str
    question: str
    answer: str
    sources_json: list[dict]
    filters_json: dict
    latency_ms: int
    feedback_score: Optional[int] = None
    created_at: datetime
