import json

from backend.core import dependencies
from backend.main import app
from backend.services import QueryService


class FailingLLMProvider:
    def generate(self, prompt: str) -> str:
        raise RuntimeError("simulated OpenAI outage")


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
    assert "evidence_summary" in query_response.json()
    assert "evidence_documents" in query_response.json()
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
    assert ".csv" in health_response.json()["supported_file_types"]

    delete_response = client.delete(f"/documents/{document_id}")
    assert delete_response.status_code == 200


def test_root_upload_alias_and_response_contract(temp_env):
    client = temp_env["client"]

    upload_response = client.post(
        "/upload",
        files={"file": ("policy.txt", b"Managers approve remote work schedules.", "text/plain")},
        data={
            "tags": json.dumps(["hr"]),
            "title": "Remote Work Policy",
            "category": "HR",
            "version": "2026.1",
        },
    )

    assert upload_response.status_code == 201
    document = upload_response.json()["document"]
    assert document["title"] == "Remote Work Policy"
    assert document["version"] == "2026.1"

    query_response = client.post("/query", json={"question": "What does the policy say?", "filters": {"categories": ["HR"]}})
    assert query_response.status_code == 200
    payload = query_response.json()
    assert payload["confidence"] in {"High", "Medium", "Low"}
    assert payload["safety"] in {"Grounded", "Limited", "None"}
    assert isinstance(payload["suggestions"], list)


def test_assistant_profiles_can_drive_query_defaults(temp_env):
    client = temp_env["client"]

    upload_response = client.post(
        "/documents/upload",
        files={"file": ("hr_policy.txt", b"Employees may work remotely two days each week with manager approval.", "text/plain")},
        data={
            "tags": json.dumps(["policy", "hr"]),
            "category": "HR",
        },
    )
    assert upload_response.status_code == 201

    assistants_response = client.get("/assistants")
    assert assistants_response.status_code == 200
    assistants = assistants_response.json()
    assert assistants

    created = client.post(
        "/assistants",
        json={
            "name": "HR Builder",
            "description": "Assistant scoped to HR policies.",
            "instructions": "Answer like an HR operations copilot and surface exceptions.",
            "tone": "compliance",
            "language": "fr",
            "answer_format": "structured",
            "categories": ["HR"],
            "latest_only": True,
            "retrieval_top_k": 6,
            "use_reranking": True,
            "published": True,
        },
    )
    assert created.status_code == 201
    assistant = created.json()
    assert assistant["categories"] == ["HR"]

    query_response = client.post(
        "/query",
        json={
            "assistant_id": assistant["id"],
            "question": "Quelle est la politique de télétravail ?",
        },
    )
    assert query_response.status_code == 200
    payload = query_response.json()
    assert payload["assistant_id"] == assistant["id"]
    assert payload["assistant_name"] == "HR Builder"
    assert payload["answer_format"] == "structured"
    assert payload["used_context_count"] >= 1


def test_query_falls_back_when_primary_llm_fails(temp_env):
    client = temp_env["client"]

    upload_response = client.post(
        "/documents/upload",
        files={"file": ("policy.txt", b"Managers approve recurring remote work schedules.", "text/plain")},
        data={
            "tags": json.dumps(["policy"]),
            "category": "HR",
        },
    )
    assert upload_response.status_code == 201

    fallback_query_service = QueryService(
        retrieval_service=temp_env["query_service"].retrieval_service,
        llm_provider=FailingLLMProvider(),
        history_repository=temp_env["history_repo"],
        documents_repository=temp_env["documents_repo"],
        assistants_repository=temp_env["assistants_repo"],
        enable_reranking=True,
        max_summary_chunks=8,
    )
    app.dependency_overrides[dependencies.get_query_service] = lambda: fallback_query_service

    query_response = client.post(
        "/query",
        json={"question": "Who approves recurring remote work schedules?"},
    )
    assert query_response.status_code == 200
    payload = query_response.json()
    assert payload["status"] == "answered"
    assert payload["used_context_count"] >= 1
