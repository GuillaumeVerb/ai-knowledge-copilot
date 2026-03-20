import re
from collections.abc import Iterable

from backend.ingestion.parser import ParsedPage


class TextChunker:
    TOKEN_PATTERN = re.compile(r"\S+")

    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        if overlap >= chunk_size:
            raise ValueError("overlap must be smaller than chunk_size")
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_pages(self, pages: Iterable[ParsedPage], *, document_id: str) -> list[dict]:
        chunks: list[dict] = []
        chunk_index = 0
        for page in pages:
            text = page.text.strip()
            if not text:
                continue
            spans = self._token_spans(text)
            if not spans:
                continue
            start_token = 0
            while start_token < len(spans):
                end_token = min(start_token + self.chunk_size, len(spans))
                char_start = spans[start_token][0]
                char_end = spans[end_token - 1][1]
                slice_text = text[char_start:char_end].strip()
                if slice_text:
                    chunks.append(
                        {
                            "chunk_index": chunk_index,
                            "text": slice_text,
                            "page_number": page.page_number,
                            "section_title": page.section_title,
                            "metadata_json": {
                                "document_id": document_id,
                                "page_number": page.page_number,
                                "section_title": page.section_title,
                                "char_start": char_start,
                                "char_end": char_end,
                                "token_start": start_token,
                                "token_end": end_token,
                            },
                        }
                    )
                    chunk_index += 1
                if end_token >= len(spans):
                    break
                start_token = max(0, end_token - self.overlap)
        return chunks

    def _token_spans(self, text: str) -> list[tuple[int, int]]:
        spans: list[tuple[int, int]] = []
        for match in self.TOKEN_PATTERN.finditer(text):
            start, end = match.span()
            token = text[start:end]
            if len(token) <= 40:
                spans.append((start, end))
                continue
            for index in range(start, end):
                spans.append((index, index + 1))
        return spans
