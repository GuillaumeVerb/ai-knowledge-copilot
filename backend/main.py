from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api import admin, documents, health, history, query, summaries
from backend.core.logging import configure_logging
from backend.core.settings import get_settings


settings = get_settings()
configure_logging(settings.log_level)

app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(health.router)
app.include_router(documents.router)
app.include_router(query.router)
app.include_router(summaries.router)
app.include_router(history.router)
app.include_router(admin.router)

