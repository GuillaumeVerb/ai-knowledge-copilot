from fastapi import APIRouter, Depends

from backend.core.dependencies import get_history_repository
from backend.models.query import HistoryItem
from backend.repositories.qa_history_repo import QueryHistoryRepository


router = APIRouter(tags=["history"])


@router.get("/history", response_model=list[HistoryItem])
def list_history(
    limit: int = 20,
    repository: QueryHistoryRepository = Depends(get_history_repository),
) -> list[HistoryItem]:
    return repository.list_entries(limit=limit)
