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
    assert payload["confidence_label"] in {"high", "medium", "low"}


def test_demo_seed_endpoint_available(temp_env):
    client = temp_env["client"]
    response = client.post("/demo/seed")
    assert response.status_code == 200
    assert "seeded" in response.json()


def test_feedback_endpoint_updates_history(temp_env):
    client = temp_env["client"]
    upload_response = client.post(
        "/documents/upload",
        files={"file": ("faq.txt", b"Vacation requests must be submitted two weeks in advance.", "text/plain")},
        data={"tags": "[\"hr\"]"},
    )
    assert upload_response.status_code == 201

    query_response = client.post(
        "/query",
        json={"question": "When should I submit vacation requests?"},
    )
    assert query_response.status_code == 200
    history_id = query_response.json()["history_id"]

    feedback_response = client.post(
        f"/history/{history_id}/feedback",
        json={"feedback_score": 1, "feedback_note": "Useful and concise"},
    )
    assert feedback_response.status_code == 200
    assert feedback_response.json()["feedback_score"] == 1

    history = client.get("/history").json()
    assert history[0]["feedback_score"] == 1
    assert history[0]["feedback_note"] == "Useful and concise"


def test_synthesize_endpoint_returns_structured_response(temp_env):
    ingestion_service = temp_env["ingestion_service"]
    client = temp_env["client"]

    left = ingestion_service.ingest_upload(
        filename="hr_policy.txt",
        mime_type="text/plain",
        content=b"Remote work is available two days per week after onboarding. Managers approve recurring schedules.",
        tags=["hr"],
        category="HR",
    )
    right = ingestion_service.ingest_upload(
        filename="security_policy.txt",
        mime_type="text/plain",
        content=b"Employees handling sensitive data must use company-managed devices and approved storage tools.",
        tags=["security"],
        category="Security",
    )

    response = client.post(
        "/query/synthesize",
        json={
            "question": "Summarize the main internal guidance across these documents",
            "document_ids": [left.document.id, right.document.id],
            "answer_format": "resume",
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "answered"
    assert len(payload["sections"]) >= 3
    assert payload["sources"]
    assert payload["history_id"]


def test_reimport_creates_new_document_version(temp_env):
    client = temp_env["client"]

    upload_response = client.post(
        "/documents/upload",
        files={"file": ("support.txt", b"Escalate critical incidents immediately.", "text/plain")},
        data={"tags": "[\"support\"]", "category": "Support", "document_date": "2026-02-01"},
    )
    assert upload_response.status_code == 201
    original = upload_response.json()["document"]

    reimport_response = client.post(
        f"/documents/{original['id']}/reimport",
        files={"file": ("support.txt", b"Escalate critical incidents immediately and notify leadership.", "text/plain")},
        data={"document_date": "2026-02-20"},
    )
    assert reimport_response.status_code == 201
    updated = reimport_response.json()["document"]

    assert updated["version_group_id"] == original["version_group_id"]
    assert updated["version_number"] == 2
    assert updated["supersedes_document_id"] == original["id"]

    latest_only = client.get("/documents", params={"include_superseded": "false"}).json()
    assert len(latest_only) == 1
    assert latest_only[0]["id"] == updated["id"]

    all_versions = client.get("/documents", params={"include_superseded": "true"}).json()
    assert len(all_versions) == 2
