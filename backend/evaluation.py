from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class DemoScenario:
    name: str
    question: str
    expected_documents: tuple[str, ...]
    expected_terms: tuple[str, ...]
    filters: dict[str, Any]


@dataclass(frozen=True)
class ScenarioResult:
    name: str
    passed: bool
    status: str
    source_count: int
    matched_documents: list[str]
    missing_documents: list[str]
    matched_terms: list[str]
    caution: str


DEMO_SCENARIOS: tuple[DemoScenario, ...] = (
    DemoScenario(
        name="remote-work-policy",
        question="What is the remote work policy?",
        expected_documents=("hr_handbook.txt",),
        expected_terms=("remote work", "two days", "manager"),
        filters={"tags": ["demo"]},
    ),
    DemoScenario(
        name="incident-escalation",
        question="How should a severity one incident be escalated?",
        expected_documents=("product_guide.md", "support_procedure.txt"),
        expected_terms=("incident commander", "severity one", "escalate"),
        filters={"tags": ["demo"]},
    ),
    DemoScenario(
        name="security-guidance",
        question="What are the key rules for handling sensitive data?",
        expected_documents=("internal_policy.txt",),
        expected_terms=("sensitive", "approved", "access"),
        filters={"tags": ["demo"]},
    ),
    DemoScenario(
        name="onboarding",
        question="What should new hires receive during onboarding?",
        expected_documents=("hr_handbook.txt",),
        expected_terms=("new hires", "onboarding"),
        filters={"tags": ["demo"]},
    ),
)


def evaluate_query_scenarios(
    ask_query: Callable[[dict[str, Any]], dict[str, Any]],
    scenarios: tuple[DemoScenario, ...] = DEMO_SCENARIOS,
) -> list[ScenarioResult]:
    results: list[ScenarioResult] = []
    for scenario in scenarios:
        payload = {
            "question": scenario.question,
            "filters": scenario.filters,
            "answer_format": "default",
        }
        response = ask_query(payload)
        sources = response.get("sources", [])
        matched_documents = sorted({source["document_name"] for source in sources if source["document_name"] in scenario.expected_documents})
        missing_documents = [document for document in scenario.expected_documents if document not in matched_documents]

        haystack = " ".join(
            [
                response.get("answer", ""),
                response.get("confidence_reason", ""),
                " ".join(section.get("content", "") for section in response.get("sections", [])),
                " ".join(" ".join(section.get("items", [])) for section in response.get("sections", [])),
                " ".join(source.get("excerpt", "") for source in sources),
            ]
        ).lower()
        matched_terms = [term for term in scenario.expected_terms if term.lower() in haystack]

        passed = (
            response.get("status") == "answered"
            and len(sources) >= 1
            and not missing_documents
            and len(matched_terms) >= max(1, len(scenario.expected_terms) - 1)
        )
        results.append(
            ScenarioResult(
                name=scenario.name,
                passed=passed,
                status=response.get("status", "unknown"),
                source_count=len(sources),
                matched_documents=matched_documents,
                missing_documents=missing_documents,
                matched_terms=matched_terms,
                caution=response.get("caution", ""),
            )
        )
    return results


def summarize_results(results: list[ScenarioResult]) -> dict[str, Any]:
    passed = [result for result in results if result.passed]
    failed = [result for result in results if not result.passed]
    return {
        "passed": len(passed),
        "failed": len(failed),
        "results": [result.__dict__ for result in results],
    }
