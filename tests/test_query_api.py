import json


def test_upload_query_summary_and_delete(temp_env):
    client = temp_env["client"]

    upload_response = client.post(
        "/documents/upload",
        files={"file": ("handbook.txt", b"Remote work is allowed two days per week.", "text/plain")},
        data={"tags": json.dumps(["hr", "policy"])},
    )
    assert upload_response.status_code == 201
    document_id = upload_response.json()["document"]["id"]

    query_response = client.post(
        "/query",
        json={"question": "What is the remote work policy?", "filters": {"tags": ["policy"]}},
    )
    assert query_response.status_code == 200
    assert query_response.json()["used_context_count"] >= 1

    summary_response = client.post(f"/documents/{document_id}/summary")
    assert summary_response.status_code == 200

    history_response = client.get("/history")
    assert history_response.status_code == 200
    assert len(history_response.json()) >= 1

    delete_response = client.delete(f"/documents/{document_id}")
    assert delete_response.status_code == 200
