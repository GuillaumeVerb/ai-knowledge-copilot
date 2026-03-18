from fastapi import APIRouter

from backend.core.dependencies import get_runtime_info

router = APIRouter(tags=["health"])


@router.get("/health")
def healthcheck() -> dict[str, object]:
    return {"status": "ok", **get_runtime_info()}
