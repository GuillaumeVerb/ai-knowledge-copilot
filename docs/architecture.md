# Architecture

## Overview

The project is split into a backend API, retrieval/indexing pipeline, persistence layer, and two frontends.

Primary components:

- `backend/`
- `frontend-react/`
- `frontend/`
- `scripts/`
- `data/demo_docs/`

## Backend Structure

### API layer

FastAPI routes live in `backend/api/`.

Key route groups:

- `health`
- `documents`
- `query`
- `summaries`
- `history`
- `admin`

### Domain logic

The main orchestration lives in `backend/services.py`.

This is where the app currently handles:

- question answering
- source narrowing
- comparison
- synthesis
- confidence calculation
- summary generation

### Ingestion

Document ingestion lives in `backend/ingestion/`.

Pipeline:

1. upload file
2. parse document
3. clean text
4. chunk text
5. persist chunks
6. embed/index vectors

### Retrieval

Retrieval lives in `backend/retrieval/`.

Current behavior:

- vector retrieval
- lexical retrieval over stored chunks
- hybrid score merge
- optional reranking

### LLM layer

The LLM abstraction lives in `backend/llm/`.

Modes:

- OpenAI Responses API
- local fallback provider

## Persistence

SQLite currently stores:

- documents
- chunks
- query history
- feedback metadata

Document metadata now includes:

- tags
- category
- document date
- version group
- version number
- superseded document link

## Request Flow

### Ask flow

1. `/query` receives question and filters
2. retrieval returns candidates
3. query service narrows context
4. LLM provider generates answer
5. source list is filtered
6. confidence is computed
7. query history entry is saved

### Compare flow

1. `/query/compare` receives two document ids
2. retrieval is constrained by each document
3. the service builds a comparison output
4. confidence and history are stored

### Synthesis flow

1. `/query/synthesize` receives multiple document ids
2. retrieval is constrained to those documents
3. the service builds a cross-document response
4. relevant sources are returned

### Versioning flow

1. `/documents/{id}/reimport` receives a new file
2. the previous document is loaded
3. the next version number is computed
4. a new document record is created
5. the new record points back to the previous one

## Frontends

### React

`frontend-react/` is the recommended portfolio frontend.

It currently exposes:

- ask
- compare
- summarize
- synthesize
- upload
- reimport
- metadata filters
- confidence
- feedback

### Streamlit

`frontend/` remains as a quick demo/dev frontend.

It is useful for local validation but is no longer the strongest presentation surface.

## Extension Points

The codebase is already shaped to support future additions such as:

- auth
- workspaces
- permissions
- external connectors
- analytics
- more advanced reranking
