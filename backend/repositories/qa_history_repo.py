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
    ) -> HistoryItem:
        entry_id = str(uuid4())
        created_at = _now()
        self.connection.execute(
            """
            INSERT INTO query_history (
                id, question, answer, sources_json, filters_json,
                latency_ms, feedback_score, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                entry_id,
                question,
                answer,
                json.dumps(sources_json),
                json.dumps(filters_json),
                latency_ms,
                feedback_score,
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

    def _row_to_history_item(self, row: sqlite3.Row) -> HistoryItem:
        return HistoryItem(
            id=row["id"],
            question=row["question"],
            answer=row["answer"],
            sources_json=json.loads(row["sources_json"] or "[]"),
            filters_json=json.loads(row["filters_json"] or "{}"),
            latency_ms=row["latency_ms"],
            feedback_score=row["feedback_score"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
