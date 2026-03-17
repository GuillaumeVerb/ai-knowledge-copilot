from backend.ingestion.chunker import TextChunker
from backend.ingestion.parser import ParsedPage


def test_chunking_stable_with_overlap():
    chunker = TextChunker(chunk_size=50, overlap=10)
    pages = [ParsedPage(text="A" * 120, page_number=1)]
    chunks = chunker.chunk_pages(pages, document_id="doc-1")

    assert len(chunks) == 3
    assert chunks[0]["metadata_json"]["char_start"] == 0
    assert chunks[1]["metadata_json"]["char_start"] == 40
