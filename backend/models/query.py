from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


AnswerFormat = Literal[
    "default",
    "resume",
    "etapes",
    "risques",
    "faq",
    "concise",
    "detailed",
    "checklist",
    "comparison",
    "summary",
    "structured",
]


LanguageCode = Literal["fr", "en", "auto"]


class QueryFilters(BaseModel):
    document_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    date_from: Optional[date] = None
    date_to: Optional[date] = None


class QueryRequest(BaseModel):
    question: str = Field(min_length=3)
    filters: QueryFilters = Field(default_factory=QueryFilters)
    top_k: Optional[int] = None
    answer_format: AnswerFormat = "default"
    use_reranking: Optional[bool] = None
    language: LanguageCode = "auto"
    conversation_history: list[dict[str, str]] = Field(default_factory=list)


class SourceSnippet(BaseModel):
    document_id: str
    document_name: str
    chunk_id: str
    excerpt: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    score: Optional[float] = None


class StructuredBlock(BaseModel):
    title: str
    kind: Literal["summary", "bullets", "numbered", "warning", "faq", "comparison"]
    content: str = ""
    items: list[str] = Field(default_factory=list)


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceSnippet]
    confidence: Literal["High", "Medium", "Low"] = "Low"
    safety: Literal["Grounded", "Limited", "None"] = "None"
    suggestions: list[str] = Field(default_factory=list)
    detected_language: Literal["fr", "en"] = "fr"
    used_context_count: int
    latency_ms: int
    status: Literal["answered", "not_found"]
    answer_format: AnswerFormat = "default"
    sections: list[StructuredBlock] = Field(default_factory=list)
    comparison_mode: bool = False
    clarification_needed: bool = False
    clarifying_question: Optional[str] = None
    confidence_label: Literal["high", "medium", "low"] = "low"
    confidence_score: float = 0.0
    confidence_reason: str = ""
    evidence_documents: list[str] = Field(default_factory=list)
    evidence_summary: str = ""
    caution: str = ""
    history_id: Optional[str] = None


class CompareDocumentsRequest(BaseModel):
    question: str = Field(min_length=3)
    left_document_id: str
    right_document_id: str
    answer_format: AnswerFormat = "comparison"
    language: LanguageCode = "auto"
    conversation_history: list[dict[str, str]] = Field(default_factory=list)


class SynthesizeDocumentsRequest(BaseModel):
    question: str = Field(min_length=3)
    document_ids: list[str] = Field(min_length=2)
    answer_format: AnswerFormat = "summary"
    language: LanguageCode = "auto"
    conversation_history: list[dict[str, str]] = Field(default_factory=list)


class HistoryItem(BaseModel):
    id: str
    question: str
    answer: str
    sources_json: list[dict]
    filters_json: dict
    latency_ms: int
    feedback_score: Optional[int] = None
    feedback_note: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class FeedbackRequest(BaseModel):
    feedback_score: Literal[1, -1]
    feedback_note: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: str
    feedback_score: int
    feedback_note: Optional[str] = None
    updated_at: datetime
