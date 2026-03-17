from backend.models.query import QueryFilters
from backend.repositories.documents_repo import DocumentsRepository
from backend.retrieval.retriever import RetrievalService
from backend.retrieval.vector_store import VectorStore


class EmptyVectorStore(VectorStore):
    def upsert(self, items):
        return None

    def search(self, query, *, top_k, filters=None):
        return []

    def delete_by_document_id(self, document_id):
        return None

    def recreate(self, items):
        return None


def test_hybrid_retrieval_falls_back_to_lexical(temp_env):
    ingestion_service = temp_env["ingestion_service"]
    documents_repo = temp_env["documents_repo"]

    ingestion_service.ingest_upload(
        filename="hr_policy.txt",
        mime_type="text/plain",
        content=b"Remote work is available up to two days per week after onboarding.",
        tags=["hr", "policy"],
    )

    retrieval_service = RetrievalService(
        vector_store=EmptyVectorStore(),
        documents_repository=documents_repo,
        reranker=None,
        default_top_k=4,
        fetch_k=8,
    )
    results = retrieval_service.retrieve(
        "What is the remote work policy?",
        filters=QueryFilters(tags=["policy"]),
        top_k=3,
        use_reranking=False,
    )

    assert results
    assert results[0].document_name == "hr_policy.txt"
