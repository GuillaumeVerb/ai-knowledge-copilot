from typing import Optional

from backend.models.query import AnswerFormat, SourceSnippet


SYSTEM_PROMPT = """
You are a production-grade internal AI knowledge copilot.
Answer only from the provided context and conversation memory.
Do not hallucinate or infer unsupported policies.
If the answer is not present in the context, say exactly that you do not know based on the available documents.
Always explain why the answer was selected, cite the document names, and surface disagreements.
Default to French unless the requested language is English.
""".strip()


def build_query_prompt(
    question: str,
    sources: list[SourceSnippet],
    answer_format: AnswerFormat,
    *,
    language: str = "fr",
    conversation_history: Optional[list[dict[str, str]]] = None,
    assistant_name: Optional[str] = None,
    assistant_instructions: Optional[str] = None,
    assistant_tone: Optional[str] = None,
) -> str:
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
        "concise": "Answer directly in 1 short paragraph using only the most relevant evidence.",
        "detailed": "Provide a detailed grounded answer with a short summary, key details, and caveats when relevant.",
        "checklist": "Provide the answer as an actionable checklist with clear steps.",
        "comparison": "Provide a structured comparison with similarities, differences, and operational implications.",
        "summary": "Provide a concise summary in 3 to 5 bullets.",
        "structured": "Provide a structured answer with headings for answer, evidence, and caveats.",
    }[answer_format]
    language_instruction = (
        "Answer in French. Keep labels, explanations, and recommendations in French."
        if language == "fr"
        else "Answer in English. Keep labels, explanations, and recommendations in English."
    )
    history_text = ""
    if conversation_history:
        turns = []
        for index, turn in enumerate(conversation_history[-4:], start=1):
            user_text = turn.get("question", "").strip()
            assistant_text = turn.get("answer", "").strip()
            if user_text or assistant_text:
                turns.append(f"[{index}] User: {user_text}\nAssistant: {assistant_text}")
        if turns:
            history_text = "Conversation memory:\n" + "\n\n".join(turns) + "\n\n"
    assistant_text = ""
    if assistant_name:
        assistant_text += f"Assistant profile: {assistant_name}\n"
    if assistant_tone:
        assistant_text += f"Preferred tone: {assistant_tone}\n"
    if assistant_instructions:
        assistant_text += f"Additional instructions:\n{assistant_instructions.strip()}\n\n"
    return (
        f"{instruction}\n"
        f"{language_instruction}\n"
        "If evidence is partial, explicitly say so.\n\n"
        f"{assistant_text}"
        f"{history_text}"
        f"Question: {question}\n\n"
        f"Context:\n" + "\n\n".join(formatted_sources)
    )


def build_summary_prompt(document_name: str, sources: list[SourceSnippet], *, language: str = "en") -> str:
    context = "\n\n".join(
        f"[{index}] {source.document_name}: {source.excerpt}"
        for index, source in enumerate(sources, start=1)
    )
    return (
        (
            f"Summarize the document '{document_name}' in French using only the following extracted context.\n\n{context}"
            if language == "fr"
            else f"Summarize the document '{document_name}' using only the following extracted context.\n\n{context}"
        )
    )


def build_compare_prompt(
    question: str,
    left_name: str,
    right_name: str,
    sources: list[SourceSnippet],
    *,
    language: str = "en",
) -> str:
    formatted_sources = []
    for index, source in enumerate(sources, start=1):
        formatted_sources.append(f"[{index}] {source.document_name}\n{source.excerpt}")
    return (
        (
            "Compare the two documents and answer in French with the structure: Resume, Similarites, Differences, Impacts operationnels.\n\n"
            if language == "fr"
            else "Compare the two documents and structure the answer with: Summary, Similarities, Differences, Operational impacts.\n\n"
        )
        + f"Question: {question}\n"
        f"Left document: {left_name}\n"
        f"Right document: {right_name}\n\n"
        "Context:\n" + "\n\n".join(formatted_sources)
    )
