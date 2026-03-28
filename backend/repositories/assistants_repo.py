from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from uuid import uuid4

from backend.models.assistant import AssistantProfileCreate, AssistantProfileRead, AssistantProfileUpdate


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AssistantProfilesRepository:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def ensure_seed_profiles(self) -> list[AssistantProfileRead]:
        existing = self.list_profiles()
        if existing:
            return existing

        seeds = [
            AssistantProfileCreate(
                name="General Knowledge Copilot",
                description="Balanced assistant for cross-team internal knowledge questions.",
                instructions="Answer with grounded evidence, highlight caveats, and keep the answer practical for internal teams.",
                tone="balanced",
                language="auto",
                answer_format="concise",
                latest_only=True,
                retrieval_top_k=5,
                use_reranking=True,
                is_default=True,
                published=True,
            ),
            AssistantProfileCreate(
                name="HR Policy Reviewer",
                description="Focused assistant for HR, onboarding, and policy interpretation.",
                instructions="Prioritize policy wording, exceptions, employee impact, and operational next steps for managers or people teams.",
                tone="compliance",
                language="fr",
                answer_format="structured",
                categories=["HR"],
                latest_only=True,
                retrieval_top_k=6,
                use_reranking=True,
                published=False,
            ),
            AssistantProfileCreate(
                name="Support Ops Assistant",
                description="Operational assistant for incidents, escalation, and runbook workflows.",
                instructions="Surface actionable steps first, then risks, escalation paths, and contradictions between procedures.",
                tone="support",
                language="auto",
                answer_format="checklist",
                categories=["Support", "Operations"],
                latest_only=True,
                retrieval_top_k=6,
                use_reranking=True,
                published=False,
            ),
        ]
        for seed in seeds:
            self.create_profile(seed)
        return self.list_profiles()

    def list_profiles(self) -> list[AssistantProfileRead]:
        rows = self.connection.execute(
            "SELECT * FROM assistant_profiles ORDER BY is_default DESC, updated_at DESC, created_at DESC"
        ).fetchall()
        return [self._row_to_profile(row) for row in rows]

    def get_profile(self, profile_id: str) -> AssistantProfileRead:
        row = self.connection.execute(
            "SELECT * FROM assistant_profiles WHERE id = ?",
            (profile_id,),
        ).fetchone()
        if row is None:
            raise KeyError(f"Assistant profile {profile_id} not found")
        return self._row_to_profile(row)

    def get_default_profile(self) -> AssistantProfileRead | None:
        row = self.connection.execute(
            """
            SELECT * FROM assistant_profiles
            ORDER BY is_default DESC, updated_at DESC, created_at DESC
            LIMIT 1
            """
        ).fetchone()
        return self._row_to_profile(row) if row is not None else None

    def create_profile(self, payload: AssistantProfileCreate) -> AssistantProfileRead:
        self._maybe_clear_default(payload.is_default or not self.list_profiles())
        profile_id = str(uuid4())
        created_at = _now()
        self.connection.execute(
            """
            INSERT INTO assistant_profiles (
                id, name, description, instructions, tone, language, answer_format,
                document_ids_json, tags_json, categories_json, latest_only, retrieval_top_k,
                use_reranking, is_default, published, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                profile_id,
                payload.name,
                payload.description,
                payload.instructions,
                payload.tone,
                payload.language,
                payload.answer_format,
                json.dumps(payload.document_ids),
                json.dumps(payload.tags),
                json.dumps(payload.categories),
                int(payload.latest_only),
                payload.retrieval_top_k,
                int(payload.use_reranking),
                int(payload.is_default or not self.get_default_profile()),
                int(payload.published),
                created_at,
                created_at,
            ),
        )
        self.connection.commit()
        return self.get_profile(profile_id)

    def update_profile(self, profile_id: str, payload: AssistantProfileUpdate) -> AssistantProfileRead:
        current = self.get_profile(profile_id)
        data = current.model_dump()
        changes = payload.model_dump(exclude_unset=True)
        data.update(changes)
        if data.get("is_default"):
            self._maybe_clear_default(True, exclude_id=profile_id)
        updated_at = _now()
        self.connection.execute(
            """
            UPDATE assistant_profiles
            SET
                name = ?,
                description = ?,
                instructions = ?,
                tone = ?,
                language = ?,
                answer_format = ?,
                document_ids_json = ?,
                tags_json = ?,
                categories_json = ?,
                latest_only = ?,
                retrieval_top_k = ?,
                use_reranking = ?,
                is_default = ?,
                published = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                data["name"],
                data["description"],
                data["instructions"],
                data["tone"],
                data["language"],
                data["answer_format"],
                json.dumps(data["document_ids"]),
                json.dumps(data["tags"]),
                json.dumps(data["categories"]),
                int(data["latest_only"]),
                data["retrieval_top_k"],
                int(data["use_reranking"]),
                int(data["is_default"]),
                int(data["published"]),
                updated_at,
                profile_id,
            ),
        )
        self.connection.commit()
        return self.get_profile(profile_id)

    def _maybe_clear_default(self, should_clear: bool, *, exclude_id: str | None = None) -> None:
        if not should_clear:
            return
        query = "UPDATE assistant_profiles SET is_default = 0"
        args: tuple[str, ...] = ()
        if exclude_id:
            query += " WHERE id != ?"
            args = (exclude_id,)
        self.connection.execute(query, args)

    def _row_to_profile(self, row: sqlite3.Row) -> AssistantProfileRead:
        return AssistantProfileRead(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            instructions=row["instructions"] or "",
            tone=row["tone"] or "balanced",
            language=row["language"] or "auto",
            answer_format=row["answer_format"] or "concise",
            document_ids=json.loads(row["document_ids_json"] or "[]"),
            tags=json.loads(row["tags_json"] or "[]"),
            categories=json.loads(row["categories_json"] or "[]"),
            latest_only=bool(row["latest_only"]),
            retrieval_top_k=int(row["retrieval_top_k"] or 5),
            use_reranking=bool(row["use_reranking"]),
            is_default=bool(row["is_default"]),
            published=bool(row["published"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
