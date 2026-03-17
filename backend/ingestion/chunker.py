from collections.abc import Iterable

from backend.ingestion.parser import ParsedPage


class TextChunker:
    def __init__(self, chunk_size: int = 900, overlap: int = 150):
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
            start = 0
            while start < len(text):
                end = min(start + self.chunk_size, len(text))
                slice_text = text[start:end].strip()
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
                                "char_start": start,
                                "char_end": end,
                            },
                        }
                    )
                    chunk_index += 1
                if end >= len(text):
                    break
                start = end - self.overlap
        return chunks
