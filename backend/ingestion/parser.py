from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from docx import Document as DocxDocument
from pypdf import PdfReader


@dataclass
class ParsedPage:
    text: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None


class UnsupportedFileTypeError(ValueError):
    pass


class DocumentParser:
    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md", ".csv"}

    def parse(self, path: Path) -> list[ParsedPage]:
        suffix = path.suffix.lower()
        if suffix not in self.SUPPORTED_EXTENSIONS:
            raise UnsupportedFileTypeError(f"Unsupported file type: {suffix}")
        if suffix == ".pdf":
            return self._parse_pdf(path)
        if suffix == ".docx":
            return self._parse_docx(path)
        if suffix == ".csv":
            return self._parse_csv(path)
        return self._parse_text(path)

    def _parse_pdf(self, path: Path) -> list[ParsedPage]:
        reader = PdfReader(str(path))
        pages: list[ParsedPage] = []
        for index, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if text:
                pages.append(ParsedPage(text=text, page_number=index))
        return pages

    def _parse_docx(self, path: Path) -> list[ParsedPage]:
        document = DocxDocument(str(path))
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        return [ParsedPage(text="\n".join(paragraphs), page_number=1)]

    def _parse_text(self, path: Path) -> list[ParsedPage]:
        text = path.read_text(encoding="utf-8")
        return [ParsedPage(text=text, page_number=1)]

    def _parse_csv(self, path: Path) -> list[ParsedPage]:
        with path.open(newline="", encoding="utf-8") as file_handle:
            reader = csv.reader(file_handle)
            rows = list(reader)

        if not rows:
            return [ParsedPage(text="", page_number=1)]

        header = rows[0]
        lines: list[str] = []
        for index, row in enumerate(rows[1:], start=1):
            pairs = []
            for position, value in enumerate(row):
                label = header[position] if position < len(header) and header[position] else f"column_{position + 1}"
                if value.strip():
                    pairs.append(f"{label}: {value.strip()}")
            if pairs:
                lines.append(f"Row {index}: " + " | ".join(pairs))

        if not lines:
            lines = [" | ".join(cell.strip() for cell in header if cell.strip())]
        return [ParsedPage(text="\n".join(lines), page_number=1)]
