import json
import sqlite3
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from backend.models.query import HistoryItem


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class QueryHistoryRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def create_entry(
        self,
        *,
        question: str,
        answer: str,
        sources_json: list[dict],
        filters_json: dict,
        latency_ms: int,
        feedback_score: Optional[int] = None,
        feedback_note: Optional[str] = None,
    ) -> HistoryItem:
        entry_id = str(uuid4())
        created_at = _now()
        self.connection.execute(
            """
            INSERT INTO query_history (
                id, question, answer, sources_json, filters_json,
                latency_ms, feedback_score, feedback_note, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry_id,
                question,
                answer,
                json.dumps(sources_json),
                json.dumps(filters_json),
                latency_ms,
                feedback_score,
                feedback_note,
                created_at,
                created_at,
            ),
        )
        self.connection.commit()
        return self.get_entry(entry_id)

    def list_entries(self, limit: int = 20) -> list[HistoryItem]:
        rows = self.connection.execute(
            "SELECT * FROM query_history ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._row_to_history_item(row) for row in rows]

    def get_entry(self, entry_id: str) -> HistoryItem:
        row = self.connection.execute(
            "SELECT * FROM query_history WHERE id = ?",
            (entry_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"History entry {entry_id} not found")
        return self._row_to_history_item(row)

    def update_feedback(
        self,
        entry_id: str,
        *,
        feedback_score: int,
        feedback_note: Optional[str] = None,
    ) -> HistoryItem:
        self.get_entry(entry_id)
        updated_at = _now()
        self.connection.execute(
            """
            UPDATE query_history
            SET feedback_score = ?, feedback_note = ?, updated_at = ?
            WHERE id = ?
            """,
            (feedback_score, feedback_note, updated_at, entry_id),
        )
        self.connection.commit()
        return self.get_entry(entry_id)

    def _row_to_history_item(self, row: sqlite3.Row) -> HistoryItem:
        return HistoryItem(
            id=row["id"],
            question=row["question"],
            answer=row["answer"],
            sources_json=json.loads(row["sources_json"] or "[]"),
            filters_json=json.loads(row["filters_json"] or "{}"),
            latency_ms=row["latency_ms"],
            feedback_score=row["feedback_score"],
            feedback_note=row["feedback_note"] if "feedback_note" in row.keys() else None,
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None,
        )
