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
