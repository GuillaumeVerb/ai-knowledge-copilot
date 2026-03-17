from backend.models.query import QueryRequest


def test_history_records_queries(temp_env):
    ingestion_service = temp_env["ingestion_service"]
    query_service = temp_env["query_service"]
    history_repo = temp_env["history_repo"]

    ingestion_service.ingest_upload(
        filename="faq.txt",
        mime_type="text/plain",
        content=b"Vacation requests must be submitted two weeks in advance.",
        tags=["hr"],
    )
    query_service.answer_query(QueryRequest(question="When should I submit vacation requests?"))
    entries = history_repo.list_entries()
    assert len(entries) == 1
