from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "AI Knowledge Copilot"
    app_env: str = "development"
    api_prefix: str = ""
    host: str = "0.0.0.0"
    port: int = 8000

    data_dir: Path = Field(default=ROOT_DIR / "data")
    upload_dir: Path = Field(default=ROOT_DIR / "data" / "uploads")
    demo_data_dir: Path = Field(default=ROOT_DIR / "data" / "demo_docs")
    sqlite_path: Path = Field(default=ROOT_DIR / "data" / "app.db")

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: Optional[str] = None
    qdrant_collection_name: str = "knowledge_chunks"

    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4.1-mini"
    embedding_model: str = "text-embedding-3-small"

    chunk_size: int = 500
    chunk_overlap: int = 100
    retrieval_top_k: int = 5
    retrieval_fetch_k: int = 10
    max_summary_chunks: int = 12
    enable_reranking: bool = True
    allow_stub_llm: bool = True

    log_level: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    settings = Settings()
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.demo_data_dir.mkdir(parents=True, exist_ok=True)
    settings.sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
