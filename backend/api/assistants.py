from fastapi import APIRouter, Depends, HTTPException, status

from backend.core.dependencies import get_assistant_repository
from backend.models.assistant import AssistantProfileCreate, AssistantProfileRead, AssistantProfileUpdate
from backend.repositories.assistants_repo import AssistantProfilesRepository


router = APIRouter(prefix="/assistants", tags=["assistants"])


@router.get("", response_model=list[AssistantProfileRead])
def list_assistants(
    repository: AssistantProfilesRepository = Depends(get_assistant_repository),
) -> list[AssistantProfileRead]:
    return repository.ensure_seed_profiles()


@router.post("", response_model=AssistantProfileRead, status_code=status.HTTP_201_CREATED)
def create_assistant(
    payload: AssistantProfileCreate,
    repository: AssistantProfilesRepository = Depends(get_assistant_repository),
) -> AssistantProfileRead:
    return repository.create_profile(payload)


@router.patch("/{assistant_id}", response_model=AssistantProfileRead)
def update_assistant(
    assistant_id: str,
    payload: AssistantProfileUpdate,
    repository: AssistantProfilesRepository = Depends(get_assistant_repository),
) -> AssistantProfileRead:
    try:
        return repository.update_profile(assistant_id, payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

