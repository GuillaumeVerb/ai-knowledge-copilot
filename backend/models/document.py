from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class DocumentCreate(BaseModel):
    filename: str
    original_filename: str
    mime_type: str
    size_bytes: int
    storage_path: str
    tags: list[str] = Field(default_factory=list)
    status: str = "uploaded"
    source_type: str = "upload"
    workspace_id: Optional[str] = None


class DocumentRead(BaseModel):
    id: str
    filename: str
    original_filename: str
    mime_type: str
    size_bytes: int
    source_type: str
    workspace_id: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    storage_path: str
    status: str
    created_at: datetime
    updated_at: datetime


class DocumentUploadResponse(BaseModel):
    document: DocumentRead
    chunks_indexed: int
    message: str


class ChunkRecord(BaseModel):
    id: str
    document_id: str
    chunk_index: int
    text: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    metadata_json: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class DeleteDocumentResponse(BaseModel):
    document_id: str
    deleted: bool
    message: str
