from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field

from backend.models.query import AnswerFormat, LanguageCode


AssistantTone = Literal["balanced", "executive", "support", "compliance", "friendly"]


class AssistantProfileBase(BaseModel):
    name: str = Field(min_length=2, max_length=80)
    description: str = Field(default="", max_length=240)
    instructions: str = Field(default="", max_length=4000)
    tone: AssistantTone = "balanced"
    language: LanguageCode = "auto"
    answer_format: AnswerFormat = "concise"
    document_ids: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    latest_only: bool = True
    retrieval_top_k: int = Field(default=5, ge=1, le=12)
    use_reranking: bool = True
    is_default: bool = False
    published: bool = False


class AssistantProfileCreate(AssistantProfileBase):
    pass


class AssistantProfileUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=2, max_length=80)
    description: Optional[str] = Field(default=None, max_length=240)
    instructions: Optional[str] = Field(default=None, max_length=4000)
    tone: Optional[AssistantTone] = None
    language: Optional[LanguageCode] = None
    answer_format: Optional[AnswerFormat] = None
    document_ids: Optional[list[str]] = None
    tags: Optional[list[str]] = None
    categories: Optional[list[str]] = None
    latest_only: Optional[bool] = None
    retrieval_top_k: Optional[int] = Field(default=None, ge=1, le=12)
    use_reranking: Optional[bool] = None
    is_default: Optional[bool] = None
    published: Optional[bool] = None


class AssistantProfileRead(AssistantProfileBase):
    id: str
    created_at: datetime
    updated_at: datetime

