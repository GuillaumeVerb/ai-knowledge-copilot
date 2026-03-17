from backend.core.settings import get_settings
from typing import Union

from fastapi import APIRouter, Depends

from backend.core.dependencies import get_ingestion_service
from backend.ingestion.indexer import DocumentIngestionService


router = APIRouter(tags=["admin"])


@router.post("/reindex")
def reindex_documents(
    ingestion_service: DocumentIngestionService = Depends(get_ingestion_service),
) -> dict[str, Union[int, str]]:
    count = ingestion_service.reindex_all()
    return {"message": "Reindex complete", "chunks_indexed": count}


@router.post("/demo/seed")
def seed_demo_documents(
    ingestion_service: DocumentIngestionService = Depends(get_ingestion_service),
) -> dict[str, Union[int, str]]:
    settings = get_settings()
    result = ingestion_service.seed_demo_documents(settings.demo_data_dir)
    return {"message": "Demo dataset processed", **result}
