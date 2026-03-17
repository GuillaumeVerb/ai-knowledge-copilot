# AI Knowledge Copilot

AI Knowledge Copilot is a portfolio-ready document intelligence assistant built to answer grounded questions across internal procedures, handbooks, support guides, and knowledge-base style content. It combines retrieval, source citations, document summaries, and document comparison in a simple product demo that can evolve into a more serious SaaS or internal tool.

## Problem

Teams lose time searching through scattered documentation, repeating the same questions, and relying on subject-matter experts for routine information retrieval. Traditional keyword search often returns too much noise and too little confidence.

## Solution

AI Knowledge Copilot provides:

- natural-language questions over uploaded documents
- grounded answers with citations
- structured summaries
- document-to-document comparison
- a lightweight but extensible architecture for future SaaS growth

The current V2 focuses on two goals at once:

- a premium portfolio demo
- a commercially credible foundation for selling knowledge copilot work

## What this proves

- RAG architecture with ingestion, chunking, retrieval, reranking, and answer generation
- product thinking beyond a raw LLM wrapper
- source-aware outputs and retrieval quality controls
- separation of backend logic from UI
- deployable local stack with tests, demo dataset, and Docker assets

## Demo highlights

- Upload `PDF`, `DOCX`, `TXT`, and `MD` documents
- Ask grounded questions with filtered source display
- Generate structured document summaries
- Compare two documents with similarities, differences, and operational implications
- Review recent query history
- Seed a demo dataset for portfolio screenshots and walkthroughs

## Stack

- Backend: FastAPI, Pydantic, SQLite
- Retrieval: Qdrant or in-memory fallback, configurable reranking
- LLM: OpenAI Responses API or local fallback mode
- Frontend: Streamlit
- Dev experience: Docker Compose, test suite, demo scripts

## Runtime modes

- Recommended demo mode: `OpenAI + Qdrant`
- Local development mode: local fallback summarization + in-memory retrieval fallback

The local fallback exists to keep the app runnable without external services, but the best client-facing demo quality comes from setting `OPENAI_API_KEY`.

## Core flows

### 1. Ask the knowledge base

- ask a question in natural language
- retrieve the most relevant chunks
- narrow context before answer generation
- return a concise answer plus only the truly relevant sources

### 2. Summarize a document

- summarize one document into an overview and key points
- keep the summary scoped to the selected document only

### 3. Compare two documents

- compare procedures or policies side by side
- surface common ground, differences, and likely operational impact

## Screenshots to capture

- document upload and indexed library
- grounded answer with one relevant source
- structured summary output
- structured comparison output

## Quick start

### Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### Start the full local demo

```bash
./scripts/start_demo.sh
```

Demo ports:

- Backend: `http://localhost:8010`
- Streamlit: `http://localhost:8502`

Stop the demo:

```bash
./scripts/stop_demo.sh
```

### Manual setup

```bash
docker compose up qdrant -d
uvicorn backend.main:app --reload
streamlit run frontend/app.py
```

## API

- `GET /health`
- `GET /documents`
- `POST /documents/upload`
- `DELETE /documents/{id}`
- `POST /documents/{id}/summary`
- `POST /query`
- `POST /query/compare`
- `GET /history`
- `POST /reindex`
- `POST /demo/seed`

## Demo script

Suggested 60 to 90 second walkthrough:

1. Show the demo dataset already loaded
2. Ask: `What is the remote work policy?`
3. Show the concise answer and single relevant source
4. Summarize the HR handbook
5. Compare `product_guide.md` and `support_procedure.txt`
6. Close on the architecture and extensibility story

## Testing

```bash
PYTHONPATH=. .venv/bin/pytest
```

## Deployment target

The app is structured to support a live demo deployment with:

- pre-seeded non-sensitive documents
- FastAPI backend
- Streamlit frontend
- environment-driven OpenAI configuration

Recommended next deployment step:

- Render or Railway for backend
- Streamlit Community Cloud or containerized deployment for frontend

## Current limitations

- no authentication or workspaces yet
- local fallback mode is less polished than OpenAI mode
- Streamlit is intentionally kept as a fast product demo, not a final SaaS frontend
- no external connectors yet

## Roadmap

### V2

- better answer structuring
- cleaner comparison output
- source narrowing
- stronger demo UX
- better portfolio packaging

### V3

- authentication
- workspaces
- permissions
- connectors
- analytics

## Repository metadata

Suggested GitHub topics:

- `rag`
- `fastapi`
- `streamlit`
- `openai`
- `knowledge-base`
- `document-search`
- `ai-assistant`
- `portfolio-project`
