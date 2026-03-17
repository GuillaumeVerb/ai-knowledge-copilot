from dataclasses import dataclass
import mimetypes
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from backend.ingestion.chunker import TextChunker
from backend.ingestion.cleaner import TextCleaner
from backend.ingestion.parser import DocumentParser
from backend.models.document import DocumentCreate, DocumentUploadResponse
from backend.repositories.documents_repo import DocumentsRepository
from backend.retrieval.vector_store import VectorStore


@dataclass
class IndexingResult:
    document_id: str
    chunks_indexed: int


class DocumentStorage:
    def __init__(self, upload_dir: Path):
        self.upload_dir = upload_dir

    def save(self, filename: str, content: bytes) -> Path:
        safe_name = f"{uuid4()}_{filename}"
        path = self.upload_dir / safe_name
        path.write_bytes(content)
        return path

    def delete(self, storage_path: str) -> None:
        path = Path(storage_path)
        if path.exists():
            path.unlink()


class DocumentIngestionService:
    def __init__(
        self,
        *,
        documents_repo: DocumentsRepository,
        parser: DocumentParser,
        cleaner: TextCleaner,
        chunker: TextChunker,
        vector_store: VectorStore,
        storage: DocumentStorage,
    ):
        self.documents_repo = documents_repo
        self.parser = parser
        self.cleaner = cleaner
        self.chunker = chunker
        self.vector_store = vector_store
        self.storage = storage

    def ingest_upload(
        self,
        *,
        filename: str,
        mime_type: str,
        content: bytes,
        tags: Optional[list[str]] = None,
    ) -> DocumentUploadResponse:
        tags = tags or []
        storage_path = self.storage.save(filename, content)
        document = self.documents_repo.create_document(
            DocumentCreate(
                filename=storage_path.name,
                original_filename=filename,
                mime_type=mime_type,
                size_bytes=len(content),
                storage_path=str(storage_path),
                tags=tags,
                status="processing",
            )
        )
        try:
            pages = self.parser.parse(storage_path)
            for page in pages:
                page.text = self.cleaner.clean(page.text)
            chunks = self.chunker.chunk_pages(pages, document_id=document.id)
            stored_chunks = self.documents_repo.store_chunks(document.id, chunks)
            vectors: list[dict[str, Any]] = []
            for chunk in stored_chunks:
                vectors.append(
                    {
                        "id": chunk.id,
                        "text": chunk.text,
                        "metadata": {
                            "document_id": document.id,
                            "document_name": document.original_filename,
                            "chunk_id": chunk.id,
                            "page_number": chunk.page_number,
                            "section_title": chunk.section_title,
                            "tags": document.tags,
                        },
                    }
                )
            self.vector_store.upsert(vectors)
            document = self.documents_repo.update_status(document.id, "indexed")
            return DocumentUploadResponse(
                document=document,
                chunks_indexed=len(stored_chunks),
                message="Document uploaded and indexed successfully.",
            )
        except Exception:
            self.documents_repo.update_status(document.id, "failed")
            raise

    def delete_document(self, document_id: str) -> None:
        document = self.documents_repo.delete_document(document_id)
        self.vector_store.delete_by_document_id(document_id)
        self.storage.delete(document.storage_path)

    def reindex_all(self) -> int:
        chunks = self.documents_repo.list_all_chunks()
        vectors: list[dict[str, Any]] = []
        for chunk in chunks:
            document = self.documents_repo.get_document(chunk.document_id)
            vectors.append(
                {
                    "id": chunk.id,
                    "text": chunk.text,
                    "metadata": {
                        "document_id": document.id,
                        "document_name": document.original_filename,
                        "chunk_id": chunk.id,
                        "page_number": chunk.page_number,
                        "section_title": chunk.section_title,
                        "tags": document.tags,
                    },
                }
            )
        self.vector_store.recreate(vectors)
        return len(vectors)

    def seed_demo_documents(self, demo_dir: Path) -> dict[str, int]:
        existing_names = {document.original_filename for document in self.documents_repo.list_documents()}
        seeded = 0
        skipped = 0
        for path in sorted(demo_dir.iterdir()):
            if not path.is_file():
                continue
            if path.name in existing_names:
                skipped += 1
                continue
            mime_type, _ = mimetypes.guess_type(str(path))
            self.ingest_upload(
                filename=path.name,
                mime_type=mime_type or "text/plain",
                content=path.read_bytes(),
                tags=["demo"],
            )
            seeded += 1
        return {"seeded": seeded, "skipped": skipped}
