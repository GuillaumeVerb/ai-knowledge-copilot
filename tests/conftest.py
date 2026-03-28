from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from backend.core import dependencies
from backend.core.database import create_connection, initialize_database
from backend.ingestion.chunker import TextChunker
from backend.ingestion.cleaner import TextCleaner
from backend.ingestion.indexer import DocumentIngestionService, DocumentStorage
from backend.ingestion.parser import DocumentParser
from backend.llm.embeddings import SimpleHashEmbeddingProvider
from backend.llm.generator import StubLLMProvider
from backend.main import app
from backend.repositories.assistants_repo import AssistantProfilesRepository
from backend.repositories.documents_repo import DocumentsRepository
from backend.repositories.qa_history_repo import QueryHistoryRepository
from backend.retrieval.reranker import KeywordOverlapReranker
from backend.retrieval.retriever import RetrievalService
from backend.retrieval.vector_store import InMemoryVectorStore
from backend.services import QueryService


@pytest.fixture()
def temp_env(tmp_path: Path):
    database_path = tmp_path / "test.db"
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    connection = create_connection(database_path)
    initialize_database(connection)

    documents_repo = DocumentsRepository(connection)
    history_repo = QueryHistoryRepository(connection)
    assistants_repo = AssistantProfilesRepository(connection)
    assistants_repo.ensure_seed_profiles()
    embedding_provider = SimpleHashEmbeddingProvider()
    vector_store = InMemoryVectorStore(embedding_provider)
    ingestion_service = DocumentIngestionService(
        documents_repo=documents_repo,
        parser=DocumentParser(),
        cleaner=TextCleaner(),
        chunker=TextChunker(chunk_size=120, overlap=20),
        vector_store=vector_store,
        storage=DocumentStorage(upload_dir),
    )
    retrieval_service = RetrievalService(
        vector_store=vector_store,
        documents_repository=documents_repo,
        reranker=KeywordOverlapReranker(),
        default_top_k=4,
        fetch_k=8,
    )
    query_service = QueryService(
        retrieval_service=retrieval_service,
        llm_provider=StubLLMProvider(),
        history_repository=history_repo,
        documents_repository=documents_repo,
        assistants_repository=assistants_repo,
        enable_reranking=True,
        max_summary_chunks=8,
    )

    app.dependency_overrides[dependencies.get_documents_repository] = lambda: documents_repo
    app.dependency_overrides[dependencies.get_history_repository] = lambda: history_repo
    app.dependency_overrides[dependencies.get_assistant_repository] = lambda: assistants_repo
    app.dependency_overrides[dependencies.get_ingestion_service] = lambda: ingestion_service
    app.dependency_overrides[dependencies.get_retrieval_service] = lambda: retrieval_service
    app.dependency_overrides[dependencies.get_query_service] = lambda: query_service

    yield {
        "connection": connection,
        "documents_repo": documents_repo,
        "history_repo": history_repo,
        "assistants_repo": assistants_repo,
        "ingestion_service": ingestion_service,
        "query_service": query_service,
        "client": TestClient(app),
    }

    app.dependency_overrides.clear()
    connection.close()
