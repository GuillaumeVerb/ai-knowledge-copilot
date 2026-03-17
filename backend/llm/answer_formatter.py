from backend.models.query import SourceSnippet


def format_citations(answer: str, sources: list[SourceSnippet]) -> str:
    if not sources:
        return answer
    citation_line = "Sources: " + ", ".join(
        f"{source.document_name}"
        + (f" p.{source.page_number}" if source.page_number else "")
        for source in sources[:3]
    )
    return f"{answer.strip()}\n\n{citation_line}"
