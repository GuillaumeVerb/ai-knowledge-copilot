from __future__ import annotations

from abc import ABC, abstractmethod
import re
from collections import defaultdict

from openai import OpenAI

from backend.llm.prompts import SYSTEM_PROMPT


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class OpenAIResponsesProvider(LLMProvider):
    def __init__(self, *, api_key: str, model: str):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, prompt: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            instructions=SYSTEM_PROMPT,
            input=prompt,
        )
        return response.output_text.strip()


class StubLLMProvider(LLMProvider):
    STOPWORDS = {
        "what", "which", "with", "that", "from", "this", "there", "have", "will", "into",
        "your", "about", "when", "where", "their", "they", "them", "then", "than", "also",
        "only", "based", "available", "document", "documents", "page", "section", "context",
        "question", "answer", "using", "used", "after", "before", "must", "should", "could",
        "would", "does", "doesnt", "dont", "cant", "not", "are", "was", "were", "been", "being",
        "the", "and", "for", "but", "you", "our", "out", "who", "why", "how", "all", "any",
        "per", "one", "two", "three", "can", "has", "had", "its", "it's", "via", "only",
        "over", "under", "than", "then", "each", "such", "just", "into", "within", "across",
        "more", "most", "much", "many", "some", "same", "very", "like", "need", "needs", "required",
    }

    def generate(self, prompt: str) -> str:
        if prompt.startswith("Summarize the document"):
            blocks = self._parse_summary_blocks(prompt)
            return self._summarize_blocks(blocks)
        if "Context:" not in prompt:
            return "I do not know based on the available documents."

        instruction, question, blocks = self._parse_query_prompt(prompt)
        if not blocks:
            return "I do not know based on the available documents."

        if self._is_compare_question(question):
            return self._compare_blocks(blocks, question)

        relevant_sentences = self._select_relevant_sentences(question, blocks)
        if not relevant_sentences:
            relevant_sentences = self._all_sentences(blocks)[:3]
        return self._format_answer(instruction, question, relevant_sentences)

    def _parse_query_prompt(self, prompt: str) -> tuple[str, str, list[dict[str, str]]]:
        instruction = prompt.splitlines()[0].strip()
        question_match = re.search(r"Question:\s*(.*?)\n\nContext:\n", prompt, re.S)
        question = question_match.group(1).strip() if question_match else ""
        context = prompt.split("Context:\n", maxsplit=1)[1].strip()
        return instruction, question, self._parse_context_blocks(context)

    def _parse_summary_blocks(self, prompt: str) -> list[dict[str, str]]:
        matches = re.findall(r"\[(\d+)\]\s+(.+?):\s+(.*?)(?=\n\n\[\d+\]\s+|\Z)", prompt, re.S)
        return [
            {"document": document.strip(), "location": "", "text": text.strip()}
            for _, document, text in matches
        ]

    def _parse_context_blocks(self, context: str) -> list[dict[str, str]]:
        matches = re.findall(r"\[(\d+)\]\s+(.+?)\s+\((.*?)\)\n(.*?)(?=\n\n\[\d+\]\s+|\Z)", context, re.S)
        return [
            {"document": document.strip(), "location": location.strip(), "text": text.strip()}
            for _, document, location, text in matches
        ]

    def _summarize_blocks(self, blocks: list[dict[str, str]]) -> str:
        sentences = self._all_sentences(blocks)
        selected = self._dedupe_preserve_order(sentences)[:3]
        if not selected:
            return "I do not know based on the available documents."
        return "Summary:\n- " + "\n- ".join(selected)

    def _compare_blocks(self, blocks: list[dict[str, str]], question: str) -> str:
        by_document: dict[str, list[str]] = defaultdict(list)
        for block in blocks:
            by_document[block["document"]].extend(self._split_sentences(block["text"]))

        documents = list(by_document.keys())[:2]
        if len(documents) < 2:
            return self._format_answer("Answer directly.", question, self._all_sentences(blocks)[:3])

        left, right = documents[0], documents[1]
        left_points = self._dedupe_preserve_order(by_document[left])[:2]
        right_points = self._dedupe_preserve_order(by_document[right])[:2]

        common_terms = self._top_terms(" ".join(by_document[left]), " ".join(by_document[right]))
        lines = [
            f"Comparison of {left} and {right}:",
            f"- Common ground: both documents focus on {common_terms}.",
            f"- {left}: " + " ".join(left_points),
            f"- {right}: " + " ".join(right_points),
        ]
        return "\n".join(lines)

    def _format_answer(self, instruction: str, question: str, sentences: list[str]) -> str:
        selected = self._dedupe_preserve_order(sentences)[:3]
        if not selected:
            return "I do not know based on the available documents."

        if "concise summary" in instruction.lower():
            return "Summary:\n- " + "\n- ".join(selected)
        if "actionable steps" in instruction.lower():
            return "\n".join(f"{index}. {sentence}" for index, sentence in enumerate(selected, start=1))
        if "risks and caveats" in instruction.lower():
            return "Risks and caveats:\n- " + "\n- ".join(selected)
        if "faq style" in instruction.lower():
            return f"Q: {question}\nA: {selected[0]}"
        return " ".join(selected)

    def _select_relevant_sentences(self, question: str, blocks: list[dict[str, str]]) -> list[str]:
        keywords = set(self._tokenize(question))
        block_scores: list[tuple[int, list[str]]] = []
        for block in blocks:
            sentences = self._split_sentences(block["text"])
            sentence_scores = []
            for sentence in sentences:
                sentence_keywords = set(self._tokenize(sentence))
                overlap = len(keywords & sentence_keywords)
                sentence_scores.append((overlap, sentence))
            total_overlap = sum(score for score, _ in sentence_scores)
            if total_overlap:
                block_scores.append((total_overlap, [sentence for _, sentence in sentence_scores]))

        if block_scores:
            block_scores.sort(key=lambda item: item[0], reverse=True)
            return block_scores[0][1][:2]

        scored: list[tuple[int, str]] = []
        for sentence in self._all_sentences(blocks):
            sentence_keywords = set(self._tokenize(sentence))
            overlap = len(keywords & sentence_keywords)
            if overlap:
                scored.append((overlap, sentence))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [sentence for _, sentence in scored[:2]]

    def _all_sentences(self, blocks: list[dict[str, str]]) -> list[str]:
        sentences: list[str] = []
        for block in blocks:
            sentences.extend(self._split_sentences(block["text"]))
        return sentences

    def _split_sentences(self, text: str) -> list[str]:
        parts = re.split(r"(?<=[.!?])\s+|\n+", text.strip())
        cleaned = []
        for part in parts:
            value = part.strip(" -#")
            if value:
                cleaned.append(value)
        return cleaned

    def _dedupe_preserve_order(self, items: list[str]) -> list[str]:
        seen = set()
        result = []
        for item in items:
            normalized = item.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            result.append(item)
        return result

    def _tokenize(self, text: str) -> list[str]:
        return [
            token
            for token in re.findall(r"[a-zA-Z]{3,}", text.lower())
            if token not in self.STOPWORDS
        ]

    def _is_compare_question(self, question: str) -> bool:
        lowered = question.lower()
        return "compare" in lowered or "difference" in lowered or "differences" in lowered

    def _top_terms(self, left_text: str, right_text: str) -> str:
        left_terms = set(self._tokenize(left_text))
        right_terms = set(self._tokenize(right_text))
        common = sorted(term for term in left_terms & right_terms if term not in {"document", "documents"})
        if not common:
            return "related operational topics"
        return ", ".join(common[:3])
