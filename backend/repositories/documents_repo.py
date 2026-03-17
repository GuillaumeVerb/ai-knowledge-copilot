import json
import sqlite3
from datetime import date, datetime, timezone
from typing import Any, Optional
from uuid import uuid4

from backend.models.document import ChunkRecord, DocumentCreate, DocumentRead


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class DocumentsRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def create_document(self, payload: DocumentCreate) -> DocumentRead:
        document_id = str(uuid4())
        created_at = _now()
        version_group_id = payload.version_group_id or document_id
        self.connection.execute(
            """
            INSERT INTO documents (
                id, filename, original_filename, mime_type, size_bytes, source_type,
                workspace_id, category, document_date, version_group_id, version_number,
                supersedes_document_id, tags, storage_path, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                payload.filename,
                payload.original_filename,
                payload.mime_type,
                payload.size_bytes,
                payload.source_type,
                payload.workspace_id,
                payload.category,
                payload.document_date.isoformat() if payload.document_date else None,
                version_group_id,
                payload.version_number,
                payload.supersedes_document_id,
                json.dumps(payload.tags),
                payload.storage_path,
                payload.status,
                created_at,
                created_at,
            ),
        )
        self.connection.commit()
        return self.get_document(document_id)

    def list_documents(
        self,
        *,
        tag: Optional[str] = None,
        status: Optional[str] = None,
        search: Optional[str] = None,
        category: Optional[str] = None,
        date_from: Optional[date] = None,
        date_to: Optional[date] = None,
        include_superseded: bool = True,
    ) -> list[DocumentRead]:
        query = "SELECT * FROM documents WHERE 1=1"
        args: list[Any] = []
        if status:
            query += " AND status = ?"
            args.append(status)
        if category:
            query += " AND category = ?"
            args.append(category)
        if date_from:
            query += " AND document_date IS NOT NULL AND document_date >= ?"
            args.append(date_from.isoformat())
        if date_to:
            query += " AND document_date IS NOT NULL AND document_date <= ?"
            args.append(date_to.isoformat())
        if search:
            query += " AND (original_filename LIKE ? OR filename LIKE ? OR category LIKE ?)"
            wildcard = f"%{search}%"
            args.extend([wildcard, wildcard, wildcard])
        rows = self.connection.execute(query + " ORDER BY created_at DESC", args).fetchall()
        documents = [self._row_to_document(row) for row in rows]
        documents = self._decorate_latest_flags(documents)
        if tag:
            documents = [document for document in documents if tag in document.tags]
        if not include_superseded:
            documents = [document for document in documents if document.is_latest_version]
        return documents

    def get_document(self, document_id: str) -> DocumentRead:
        row = self.connection.execute(
            "SELECT * FROM documents WHERE id = ?",
            (document_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Document {document_id} not found")
        return self._decorate_latest_flags([self._row_to_document(row)])[0]

    def get_latest_version(self, version_group_id: str) -> DocumentRead:
        row = self.connection.execute(
            """
            SELECT * FROM documents
            WHERE version_group_id = ?
            ORDER BY version_number DESC, created_at DESC
            LIMIT 1
            """,
            (version_group_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Version group {version_group_id} not found")
        return self._decorate_latest_flags([self._row_to_document(row)])[0]

    def get_next_version_number(self, version_group_id: str) -> int:
        row = self.connection.execute(
            "SELECT MAX(version_number) AS max_version FROM documents WHERE version_group_id = ?",
            (version_group_id,),
        ).fetchone()
        max_version = row["max_version"] if row and row["max_version"] is not None else 0
        return int(max_version) + 1

    def update_status(self, document_id: str, status: str) -> DocumentRead:
        self.connection.execute(
            "UPDATE documents SET status = ?, updated_at = ? WHERE id = ?",
            (status, _now(), document_id),
        )
        self.connection.commit()
        return self.get_document(document_id)

    def replace_tags(self, document_id: str, tags: list[str]) -> DocumentRead:
        self.connection.execute(
            "UPDATE documents SET tags = ?, updated_at = ? WHERE id = ?",
            (json.dumps(tags), _now(), document_id),
        )
        self.connection.commit()
        return self.get_document(document_id)

    def delete_document(self, document_id: str) -> DocumentRead:
        document = self.get_document(document_id)
        self.connection.execute("DELETE FROM chunks WHERE document_id = ?", (document_id,))
        self.connection.execute("DELETE FROM documents WHERE id = ?", (document_id,))
        self.connection.commit()
        return document

    def store_chunks(self, document_id: str, chunks: list[dict[str, Any]]) -> list[ChunkRecord]:
        created_at = _now()
        records: list[ChunkRecord] = []
        for chunk in chunks:
            chunk_id = str(uuid4())
            self.connection.execute(
                """
                INSERT INTO chunks (
                    id, document_id, chunk_index, text, page_number, section_title,
                    metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    chunk_id,
                    document_id,
                    chunk["chunk_index"],
                    chunk["text"],
                    chunk.get("page_number"),
                    chunk.get("section_title"),
                    json.dumps(chunk.get("metadata_json", {})),
                    created_at,
                ),
            )
            records.append(
                ChunkRecord(
                    id=chunk_id,
                    document_id=document_id,
                    chunk_index=chunk["chunk_index"],
                    text=chunk["text"],
                    page_number=chunk.get("page_number"),
                    section_title=chunk.get("section_title"),
                    metadata_json=chunk.get("metadata_json", {}),
                    created_at=datetime.fromisoformat(created_at),
                )
            )
        self.connection.commit()
        return records

    def list_chunks_for_document(self, document_id: str) -> list[ChunkRecord]:
        rows = self.connection.execute(
            "SELECT * FROM chunks WHERE document_id = ? ORDER BY chunk_index ASC",
            (document_id,),
        ).fetchall()
        return [self._row_to_chunk(row) for row in rows]

    def list_all_chunks(self) -> list[ChunkRecord]:
        rows = self.connection.execute("SELECT * FROM chunks ORDER BY created_at ASC").fetchall()
        return [self._row_to_chunk(row) for row in rows]

    def _row_to_document(self, row: sqlite3.Row) -> DocumentRead:
        return DocumentRead(
            id=row["id"],
            filename=row["filename"],
            original_filename=row["original_filename"],
            mime_type=row["mime_type"],
            size_bytes=row["size_bytes"],
            source_type=row["source_type"],
            workspace_id=row["workspace_id"],
            category=row["category"],
            document_date=date.fromisoformat(row["document_date"]) if row["document_date"] else None,
            version_group_id=row["version_group_id"],
            version_number=row["version_number"] or 1,
            supersedes_document_id=row["supersedes_document_id"],
            tags=json.loads(row["tags"] or "[]"),
            storage_path=row["storage_path"],
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    def _row_to_chunk(self, row: sqlite3.Row) -> ChunkRecord:
        return ChunkRecord(
            id=row["id"],
            document_id=row["document_id"],
            chunk_index=row["chunk_index"],
            text=row["text"],
            page_number=row["page_number"],
            section_title=row["section_title"],
            metadata_json=json.loads(row["metadata_json"] or "{}"),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def _decorate_latest_flags(self, documents: list[DocumentRead]) -> list[DocumentRead]:
        if not documents:
            return []
        latest_versions: dict[str, int] = {}
        for row in self.connection.execute(
            "SELECT version_group_id, MAX(version_number) AS max_version FROM documents GROUP BY version_group_id"
        ).fetchall():
            latest_versions[row["version_group_id"]] = int(row["max_version"] or 1)
        return [
            document.model_copy(
                update={
                    "is_latest_version": document.version_number
                    >= latest_versions.get(document.version_group_id or document.id, document.version_number)
                }
            )
            for document in documents
        ]
