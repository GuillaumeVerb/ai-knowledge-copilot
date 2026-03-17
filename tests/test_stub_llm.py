from backend.llm.generator import StubLLMProvider
from backend.llm.prompts import build_query_prompt, build_summary_prompt
from backend.models.query import SourceSnippet


def test_stub_llm_produces_summary_like_answer():
    provider = StubLLMProvider()
    sources = [
        SourceSnippet(
            document_id="doc-1",
            document_name="hr_handbook.txt",
            chunk_id="chunk-1",
            excerpt="Remote work is available up to two days per week for full-time employees. Managers must approve recurring remote schedules.",
            page_number=1,
            section_title=None,
            score=0.9,
        )
    ]
    prompt = build_query_prompt("What is the remote work policy?", sources, "default")
    answer = provider.generate(prompt)

    assert "Draft answer generated" not in answer
    assert "remote work" in answer.lower()


def test_stub_llm_produces_document_summary():
    provider = StubLLMProvider()
    sources = [
        SourceSnippet(
            document_id="doc-1",
            document_name="hr_handbook.txt",
            chunk_id="chunk-1",
            excerpt="Vacation requests should be submitted at least two weeks in advance. New hires receive an onboarding checklist.",
            page_number=1,
            section_title=None,
            score=0.9,
        )
    ]
    prompt = build_summary_prompt("hr_handbook.txt", sources)
    answer = provider.generate(prompt)

    assert "## Overview" in answer
    assert "Vacation requests" in answer
