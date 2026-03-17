from fastapi import APIRouter, Depends
from fastapi import HTTPException

from backend.core.dependencies import get_history_repository
from backend.models.query import FeedbackRequest, FeedbackResponse, HistoryItem
from backend.repositories.qa_history_repo import QueryHistoryRepository


router = APIRouter(tags=["history"])


@router.get("/history", response_model=list[HistoryItem])
def list_history(
    limit: int = 20,
    repository: QueryHistoryRepository = Depends(get_history_repository),
) -> list[HistoryItem]:
    return repository.list_entries(limit=limit)


@router.post("/history/{entry_id}/feedback", response_model=FeedbackResponse)
def submit_feedback(
    entry_id: str,
    payload: FeedbackRequest,
    repository: QueryHistoryRepository = Depends(get_history_repository),
) -> FeedbackResponse:
    try:
        updated = repository.update_feedback(
            entry_id,
            feedback_score=payload.feedback_score,
            feedback_note=payload.feedback_note,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FeedbackResponse(
        id=updated.id,
        feedback_score=updated.feedback_score or payload.feedback_score,
        feedback_note=updated.feedback_note,
        updated_at=updated.updated_at or updated.created_at,
    )
