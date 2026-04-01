from __future__ import annotations

import logging
import sqlite3
from functools import lru_cache

from qdrant_client import QdrantClient

from backend.core.database import create_connection, initialize_database
from backend.core.settings import Settings, get_settings
from backend.ingestion.chunker import TextChunker
from backend.ingestion.cleaner import TextCleaner
from backend.ingestion.indexer import DocumentIngestionService, DocumentStorage
from backend.ingestion.parser import DocumentParser
from backend.llm.embeddings import OpenAIEmbeddingProvider, SimpleHashEmbeddingProvider
from backend.llm.generator import OpenAIResponsesProvider, StubLLMProvider
from backend.repositories.assistants_repo import AssistantProfilesRepository
from backend.repositories.documents_repo import DocumentsRepository
from backend.repositories.qa_history_repo import QueryHistoryRepository
from backend.retrieval.reranker import KeywordOverlapReranker
from backend.retrieval.retriever import RetrievalService
from backend.retrieval.vector_store import InMemoryVectorStore, QdrantVectorStore
from backend.services import QueryService


logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_sqlite_connection() -> sqlite3.Connection:
    settings = get_settings()
    connection = create_connection(settings.sqlite_path)
    initialize_database(connection)
    return connection


def get_documents_repository() -> DocumentsRepository:
    return DocumentsRepository(get_sqlite_connection())


def get_history_repository() -> QueryHistoryRepository:
    return QueryHistoryRepository(get_sqlite_connection())


def get_assistant_repository() -> AssistantProfilesRepository:
    repository = AssistantProfilesRepository(get_sqlite_connection())
    repository.ensure_seed_profiles()
    return repository


@lru_cache(maxsize=1)
def get_embedding_provider():
    settings = get_settings()
    if settings.openai_api_key:
        return OpenAIEmbeddingProvider(api_key=settings.openai_api_key, model=settings.embedding_model)
    return SimpleHashEmbeddingProvider()


@lru_cache(maxsize=1)
def get_vector_store():
    settings = get_settings()
    embedding_provider = get_embedding_provider()
    try:
        if settings.qdrant_url:
            client = QdrantClient(
                url=settings.qdrant_url,
                api_key=settings.qdrant_api_key,
                timeout=10,
                check_compatibility=False,
            )
            return QdrantVectorStore(
                client=client,
                collection_name=settings.qdrant_collection_name,
                embedding_provider=embedding_provider,
                vector_size=1536 if settings.openai_api_key else 64,
            )
    except Exception as exc:
        logger.warning("Qdrant unavailable, falling back to in-memory store: %s", exc)
    return InMemoryVectorStore(embedding_provider=embedding_provider)


@lru_cache(maxsize=1)
def get_llm_provider():
    settings = get_settings()
    if settings.openai_api_key:
        return OpenAIResponsesProvider(api_key=settings.openai_api_key, model=settings.openai_model)
    return StubLLMProvider()


def get_ingestion_service() -> DocumentIngestionService:
    settings = get_settings()
    return DocumentIngestionService(
        documents_repo=get_documents_repository(),
        parser=DocumentParser(),
        cleaner=TextCleaner(),
        chunker=TextChunker(chunk_size=settings.chunk_size, overlap=settings.chunk_overlap),
        vector_store=get_vector_store(),
        storage=DocumentStorage(settings.upload_dir),
    )


def get_retrieval_service() -> RetrievalService:
    settings = get_settings()
    return RetrievalService(
        vector_store=get_vector_store(),
        documents_repository=get_documents_repository(),
        reranker=KeywordOverlapReranker(),
        default_top_k=settings.retrieval_top_k,
        fetch_k=settings.retrieval_fetch_k,
    )


def get_query_service() -> QueryService:
    settings = get_settings()
    return QueryService(
        retrieval_service=get_retrieval_service(),
        llm_provider=get_llm_provider(),
        history_repository=get_history_repository(),
        documents_repository=get_documents_repository(),
        assistants_repository=get_assistant_repository(),
        enable_reranking=settings.enable_reranking,
        max_summary_chunks=settings.max_summary_chunks,
    )


def get_runtime_info() -> dict[str, str]:
    settings = get_settings()
    llm_mode = "openai" if settings.openai_api_key else "local-fallback"
    vector_store = get_vector_store()
    retrieval_mode = "qdrant" if isinstance(vector_store, QdrantVectorStore) else "in-memory"
    return {
        "llm_mode": llm_mode,
        "retrieval_mode": retrieval_mode,
        "recommended_mode": "openai",
        "supported_file_types": sorted(DocumentParser.SUPPORTED_EXTENSIONS),
    }
