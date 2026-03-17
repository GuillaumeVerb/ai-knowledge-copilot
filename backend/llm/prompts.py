from backend.models.query import AnswerFormat, SourceSnippet


SYSTEM_PROMPT = """
You are a knowledge assistant for internal documents.
Answer only from the provided context.
If the answer is not present in the context, explicitly say that you do not know based on the available documents.
Always cite source document names and relevant excerpts.
If documents disagree, state the disagreement clearly.
Keep the answer concise, useful, and structured.
""".strip()


def build_query_prompt(question: str, sources: list[SourceSnippet], answer_format: AnswerFormat) -> str:
    formatted_sources = []
    for index, source in enumerate(sources, start=1):
        location = []
        if source.page_number:
            location.append(f"page {source.page_number}")
        if source.section_title:
            location.append(f"section {source.section_title}")
        location_text = ", ".join(location) if location else "location unknown"
        formatted_sources.append(
            f"[{index}] {source.document_name} ({location_text})\n{source.excerpt}"
        )
    instruction = {
        "default": "Answer directly in 1 short paragraph using only the most relevant evidence.",
        "resume": "Provide a concise summary in 3 to 5 bullets.",
        "etapes": "Provide the answer as actionable numbered steps.",
        "risques": "Highlight the main risks and caveats in bullets.",
        "faq": "Answer in short FAQ style with a direct answer.",
    }[answer_format]
    return (
        f"{instruction}\n\n"
        f"Question: {question}\n\n"
        f"Context:\n" + "\n\n".join(formatted_sources)
    )


def build_summary_prompt(document_name: str, sources: list[SourceSnippet]) -> str:
    context = "\n\n".join(
        f"[{index}] {source.document_name}: {source.excerpt}"
        for index, source in enumerate(sources, start=1)
    )
    return (
        f"Summarize the document '{document_name}' using only the following extracted context.\n\n{context}"
    )


def build_compare_prompt(question: str, left_name: str, right_name: str, sources: list[SourceSnippet]) -> str:
    formatted_sources = []
    for index, source in enumerate(sources, start=1):
        formatted_sources.append(f"[{index}] {source.document_name}\n{source.excerpt}")
    return (
        "Compare the two documents and structure the answer with: Summary, Similarities, Differences, Implications.\n\n"
        f"Question: {question}\n"
        f"Left document: {left_name}\n"
        f"Right document: {right_name}\n\n"
        "Context:\n" + "\n\n".join(formatted_sources)
    )
