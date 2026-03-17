import json
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from backend.core.dependencies import get_documents_repository, get_ingestion_service
from backend.models.document import DeleteDocumentResponse, DocumentRead, DocumentUploadResponse
from backend.repositories.documents_repo import DocumentsRepository
from backend.ingestion.indexer import DocumentIngestionService


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    tags: str = Form(default="[]"),
    ingestion_service: DocumentIngestionService = Depends(get_ingestion_service),
) -> DocumentUploadResponse:
    try:
        parsed_tags = json.loads(tags)
        if not isinstance(parsed_tags, list):
            raise ValueError
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="tags must be a JSON array") from exc
    content = await file.read()
    try:
        return ingestion_service.ingest_upload(
            filename=file.filename or "document",
            mime_type=file.content_type or "application/octet-stream",
            content=content,
            tags=[str(tag) for tag in parsed_tags],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("", response_model=list[DocumentRead])
def list_documents(
    tag: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    repository: DocumentsRepository = Depends(get_documents_repository),
) -> list[DocumentRead]:
    return repository.list_documents(tag=tag, status=status, search=search)


@router.delete("/{document_id}", response_model=DeleteDocumentResponse)
def delete_document(
    document_id: str,
    ingestion_service: DocumentIngestionService = Depends(get_ingestion_service),
) -> DeleteDocumentResponse:
    try:
        ingestion_service.delete_document(document_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return DeleteDocumentResponse(
        document_id=document_id,
        deleted=True,
        message="Document deleted successfully.",
    )
