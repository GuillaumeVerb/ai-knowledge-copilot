from fastapi import APIRouter, Depends, HTTPException

from backend.core.dependencies import get_query_service
from backend.models.answer import DocumentSummaryResponse
from backend.services import QueryService


router = APIRouter(tags=["summaries"])


@router.post("/documents/{document_id}/summary", response_model=DocumentSummaryResponse)
def summarize_document(
    document_id: str,
    query_service: QueryService = Depends(get_query_service),
) -> DocumentSummaryResponse:
    try:
        return query_service.summarize_document(document_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
