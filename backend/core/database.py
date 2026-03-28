import sqlite3
from contextlib import contextmanager
from pathlib import Path


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    title TEXT,
    mime_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'upload',
    workspace_id TEXT,
    category TEXT,
    document_date TEXT,
    version TEXT,
    version_group_id TEXT,
    version_number INTEGER NOT NULL DEFAULT 1,
    supersedes_document_id TEXT,
    tags TEXT NOT NULL DEFAULT '[]',
    storage_path TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS chunks (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    text TEXT NOT NULL,
    page_number INTEGER,
    section_title TEXT,
    metadata_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    FOREIGN KEY(document_id) REFERENCES documents(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS query_history (
    id TEXT PRIMARY KEY,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    sources_json TEXT NOT NULL DEFAULT '[]',
    filters_json TEXT NOT NULL DEFAULT '{}',
    latency_ms INTEGER NOT NULL DEFAULT 0,
    feedback_score INTEGER,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS assistant_profiles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    instructions TEXT NOT NULL DEFAULT '',
    tone TEXT NOT NULL DEFAULT 'balanced',
    language TEXT NOT NULL DEFAULT 'auto',
    answer_format TEXT NOT NULL DEFAULT 'concise',
    document_ids_json TEXT NOT NULL DEFAULT '[]',
    tags_json TEXT NOT NULL DEFAULT '[]',
    categories_json TEXT NOT NULL DEFAULT '[]',
    latest_only INTEGER NOT NULL DEFAULT 1,
    retrieval_top_k INTEGER NOT NULL DEFAULT 5,
    use_reranking INTEGER NOT NULL DEFAULT 1,
    is_default INTEGER NOT NULL DEFAULT 0,
    published INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_query_history_created_at ON query_history(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_assistant_profiles_updated_at ON assistant_profiles(updated_at DESC);
"""


def create_connection(db_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(db_path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON;")
    return connection


def initialize_database(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA_SQL)
    _ensure_column(connection, "documents", "category", "TEXT")
    _ensure_column(connection, "documents", "document_date", "TEXT")
    _ensure_column(connection, "documents", "title", "TEXT")
    _ensure_column(connection, "documents", "version", "TEXT")
    _ensure_column(connection, "documents", "version_group_id", "TEXT")
    _ensure_column(connection, "documents", "version_number", "INTEGER NOT NULL DEFAULT 1")
    _ensure_column(connection, "documents", "supersedes_document_id", "TEXT")
    _ensure_column(connection, "query_history", "feedback_note", "TEXT")
    _ensure_column(connection, "query_history", "updated_at", "TEXT")
    _ensure_column(connection, "assistant_profiles", "description", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(connection, "assistant_profiles", "instructions", "TEXT NOT NULL DEFAULT ''")
    _ensure_column(connection, "assistant_profiles", "tone", "TEXT NOT NULL DEFAULT 'balanced'")
    _ensure_column(connection, "assistant_profiles", "language", "TEXT NOT NULL DEFAULT 'auto'")
    _ensure_column(connection, "assistant_profiles", "answer_format", "TEXT NOT NULL DEFAULT 'concise'")
    _ensure_column(connection, "assistant_profiles", "document_ids_json", "TEXT NOT NULL DEFAULT '[]'")
    _ensure_column(connection, "assistant_profiles", "tags_json", "TEXT NOT NULL DEFAULT '[]'")
    _ensure_column(connection, "assistant_profiles", "categories_json", "TEXT NOT NULL DEFAULT '[]'")
    _ensure_column(connection, "assistant_profiles", "latest_only", "INTEGER NOT NULL DEFAULT 1")
    _ensure_column(connection, "assistant_profiles", "retrieval_top_k", "INTEGER NOT NULL DEFAULT 5")
    _ensure_column(connection, "assistant_profiles", "use_reranking", "INTEGER NOT NULL DEFAULT 1")
    _ensure_column(connection, "assistant_profiles", "is_default", "INTEGER NOT NULL DEFAULT 0")
    _ensure_column(connection, "assistant_profiles", "published", "INTEGER NOT NULL DEFAULT 0")
    connection.execute(
        """
        UPDATE documents
        SET version_group_id = id
        WHERE version_group_id IS NULL OR version_group_id = ''
        """
    )
    connection.execute(
        """
        UPDATE assistant_profiles
        SET is_default = CASE
            WHEN id = (
                SELECT id FROM assistant_profiles
                ORDER BY is_default DESC, updated_at DESC, created_at DESC
                LIMIT 1
            ) THEN 1
            ELSE 0
        END
        WHERE EXISTS (SELECT 1 FROM assistant_profiles)
        """
    )
    connection.commit()


def _ensure_column(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_definition: str,
) -> None:
    existing_columns = {
        row["name"]
        for row in connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    }
    if column_name in existing_columns:
        return
    connection.execute(
        f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition}"
    )


@contextmanager
def transaction(connection: sqlite3.Connection):
    try:
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
