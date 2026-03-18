from backend.evaluation import evaluate_query_scenarios, summarize_results


def test_demo_evaluation_scenarios_pass_with_seeded_style_documents(temp_env):
    ingestion_service = temp_env["ingestion_service"]
    client = temp_env["client"]

    fixtures = {
        "hr_handbook.txt": b"Remote work is available up to two days per week for full-time employees after the first month of onboarding. Managers must approve recurring remote schedules. New hires receive a checklist covering equipment, payroll, security training, and team introductions.",
        "internal_policy.txt": b"Sensitive documents should be stored in approved systems only. Access requests must be reviewed by the team manager and security contact.",
        "product_guide.md": b"Severity one incidents require immediate paging of the on-call engineer and notification of the incident commander.",
        "support_procedure.txt": b"If an outage affects more than one customer, escalate to the incident commander immediately. Support agents should collect account ID and issue summary before escalating a ticket.",
    }
    for filename, content in fixtures.items():
        ingestion_service.ingest_upload(
            filename=filename,
            mime_type="text/plain",
            content=content,
            tags=["demo"],
        )

    results = evaluate_query_scenarios(lambda payload: client.post("/query", json=payload).json())
    summary = summarize_results(results)

    assert summary["failed"] == 0
    assert summary["passed"] >= 4
