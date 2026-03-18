from pydantic import BaseModel, Field

from backend.models.query import SourceSnippet, StructuredBlock


class DocumentSummaryResponse(BaseModel):
    document_id: str
    summary: str
    sources: list[SourceSnippet]
    latency_ms: int
    sections: list[StructuredBlock] = Field(default_factory=list)
    evidence_documents: list[str] = Field(default_factory=list)
    evidence_summary: str = ""
