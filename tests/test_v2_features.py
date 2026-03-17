def test_compare_response_returns_structured_sections(temp_env):
    ingestion_service = temp_env["ingestion_service"]
    client = temp_env["client"]

    left = ingestion_service.ingest_upload(
        filename="product_guide.md",
        mime_type="text/markdown",
        content=b"Severity one incidents require immediate paging of the on-call engineer.",
        tags=["product", "support"],
    )
    right = ingestion_service.ingest_upload(
        filename="support_procedure.txt",
        mime_type="text/plain",
        content=b"Support agents collect details first, then escalate to the incident commander for broader outages.",
        tags=["support", "operations"],
    )

    response = client.post(
        "/query/compare",
        json={
            "question": "Compare incident escalation procedures",
            "left_document_id": left.document.id,
            "right_document_id": right.document.id,
            "answer_format": "default",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["comparison_mode"] is True
    assert len(payload["sections"]) >= 3
    assert payload["sources"]


def test_demo_seed_endpoint_available(temp_env):
    client = temp_env["client"]
    response = client.post("/demo/seed")
    assert response.status_code == 200
    assert "seeded" in response.json()
