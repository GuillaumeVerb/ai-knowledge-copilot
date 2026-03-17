# AI Knowledge Copilot

AI Knowledge Copilot is a document-focused RAG assistant built with FastAPI, Streamlit, SQLite, OpenAI, and Qdrant. It lets teams upload internal documents, ask grounded questions, review cited sources, summarize documents, compare documents, and inspect recent query history.

## Features

- Upload and index `PDF`, `DOCX`, `TXT`, and `MD` files
- Chunking with metadata for page-level citations
- Vector search with `Qdrant`
- Grounded Q&A with sources
- Document summaries
- Document comparison
- Query history
- Streamlit demo UI
- Dockerized local stack

## Project structure

```text
backend/
  api/
  core/
  ingestion/
  llm/
  models/
  repositories/
  retrieval/
frontend/
data/
tests/
docker/
```

## Prerequisites

- Python 3.9+
- Docker and Docker Compose for the full local stack
- Optional: OpenAI API key for production-grade embeddings and responses

## Local setup

1. Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy the environment file:

```bash
cp .env.example .env
```

3. Start Qdrant:

```bash
docker compose up qdrant -d
```

4. Run the backend:

```bash
uvicorn backend.main:app --reload
```

5. Run the frontend:

```bash
streamlit run frontend/app.py
```

## Quick demo flow

If you want the seeded portfolio demo flow:

```bash
cp .env.example .env
./scripts/start_demo.sh
```

This will:

- start the FastAPI backend
- seed the demo documents from `data/demo_docs/`
- start the demo on dedicated ports to avoid local conflicts:
  - backend: `http://localhost:8010`
  - Streamlit: `http://localhost:8502`

To stop both services:

```bash
./scripts/stop_demo.sh
```

## Docker setup

```bash
cp .env.example .env
docker compose up --build
```

Frontend: `http://localhost:8501`

Backend API: `http://localhost:8000`

Qdrant: `http://localhost:6333`

## API endpoints

- `GET /health`
- `POST /documents/upload`
- `GET /documents`
- `DELETE /documents/{id}`
- `POST /query`
- `POST /query/compare`
- `POST /documents/{id}/summary`
- `GET /history`
- `POST /reindex`

## Environment variables

- `OPENAI_API_KEY`: optional. If omitted, the app falls back to a stub LLM and hash-based embeddings for local development/tests.
- `OPENAI_MODEL`: default response model.
- `EMBEDDING_MODEL`: default embeddings model.
- `QDRANT_URL`: Qdrant endpoint.
- `SQLITE_PATH`: local metadata database path.
- `UPLOAD_DIR`: uploaded files location.

## Testing

```bash
PYTHONPATH=. .venv/bin/pytest
```

## Demo dataset

Add non-sensitive showcase documents in `data/demo_docs/`. The repository already includes seed demo files for HR, support, product, internal policy, and reporting use cases.

You can seed them manually with:

```bash
PYTHONPATH=. .venv/bin/python scripts/seed_demo_data.py
```

## Notes

- The business logic lives in FastAPI services and repositories, not in Streamlit, so the backend can later be reused by a React frontend.
- The LLM, embeddings, and vector store are abstracted enough to support future provider changes.
- Current V2 implementation includes filters, comparison, reranking, and structured answer formats.
