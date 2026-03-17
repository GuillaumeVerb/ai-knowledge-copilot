from backend.models.query import QueryFilters, QueryRequest


def test_retrieval_with_tag_filter(temp_env):
    ingestion_service = temp_env["ingestion_service"]
    query_service = temp_env["query_service"]

    ingestion_service.ingest_upload(
        filename="support.txt",
        mime_type="text/plain",
        content=b"Escalation policy: page the on-call engineer for severity one incidents.",
        tags=["support"],
    )

    response = query_service.answer_query(
        QueryRequest(
            question="How do we escalate a severity one incident?",
            filters=QueryFilters(tags=["support"]),
        )
    )
    assert response.status == "answered"
    assert response.used_context_count >= 1
