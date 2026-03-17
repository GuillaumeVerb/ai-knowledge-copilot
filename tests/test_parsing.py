from pathlib import Path

from docx import Document as DocxDocument
from pypdf import PdfWriter

from backend.ingestion.parser import DocumentParser


def test_parse_txt(tmp_path: Path):
    path = tmp_path / "sample.txt"
    path.write_text("hello world", encoding="utf-8")
    pages = DocumentParser().parse(path)
    assert pages[0].text == "hello world"


def test_parse_docx(tmp_path: Path):
    path = tmp_path / "sample.docx"
    doc = DocxDocument()
    doc.add_paragraph("Employee handbook")
    doc.save(path)
    pages = DocumentParser().parse(path)
    assert "Employee handbook" in pages[0].text


def test_parse_pdf(tmp_path: Path):
    path = tmp_path / "sample.pdf"
    writer = PdfWriter()
    writer.add_blank_page(width=100, height=100)
    with path.open("wb") as file_handle:
        writer.write(file_handle)
    pages = DocumentParser().parse(path)
    assert isinstance(pages, list)
