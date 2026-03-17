import json


def test_upload_query_summary_and_delete(temp_env):
    client = temp_env["client"]

    upload_response = client.post(
        "/documents/upload",
        files={"file": ("handbook.txt", b"Remote work is allowed two days per week.", "text/plain")},
        data={
            "tags": json.dumps(["hr", "policy"]),
            "category": "HR",
            "document_date": "2026-01-10",
        },
    )
    assert upload_response.status_code == 201
    document_id = upload_response.json()["document"]["id"]
    assert upload_response.json()["document"]["category"] == "HR"
    assert upload_response.json()["document"]["document_date"] == "2026-01-10"

    documents_response = client.get("/documents", params={"category": "HR", "date_from": "2026-01-01"})
    assert documents_response.status_code == 200
    assert len(documents_response.json()) == 1

    query_response = client.post(
        "/query",
        json={"question": "What is the remote work policy?", "filters": {"tags": ["policy"]}},
    )
    assert query_response.status_code == 200
    assert query_response.json()["used_context_count"] >= 1
    assert query_response.json()["sections"]
    assert query_response.json()["confidence_label"] in {"high", "medium", "low"}
    assert "confidence_reason" in query_response.json()
    assert query_response.json()["history_id"]

    summary_response = client.post(f"/documents/{document_id}/summary")
    assert summary_response.status_code == 200
    assert summary_response.json()["sections"]

    history_response = client.get("/history")
    assert history_response.status_code == 200
    assert len(history_response.json()) >= 1

    health_response = client.get("/health")
    assert health_response.status_code == 200
    assert "llm_mode" in health_response.json()

    delete_response = client.delete(f"/documents/{document_id}")
    assert delete_response.status_code == 200
