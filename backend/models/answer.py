from pydantic import BaseModel

from backend.models.query import SourceSnippet


class DocumentSummaryResponse(BaseModel):
    document_id: str
    summary: str
    sources: list[SourceSnippet]
    latency_ms: int
