from fastapi import APIRouter, Depends, HTTPException

from backend.core.dependencies import get_query_service
from backend.models.query import CompareDocumentsRequest, QueryRequest, QueryResponse
from backend.services import QueryService


router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
def query_documents(
    request: QueryRequest,
    query_service: QueryService = Depends(get_query_service),
) -> QueryResponse:
    return query_service.answer_query(request)


@router.post("/query/compare", response_model=QueryResponse)
def compare_documents(
    request: CompareDocumentsRequest,
    query_service: QueryService = Depends(get_query_service),
) -> QueryResponse:
    try:
        return query_service.compare_documents(request)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
