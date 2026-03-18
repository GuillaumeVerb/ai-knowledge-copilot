# Architecture

AI Knowledge Copilot is intentionally small enough to understand quickly, but structured enough to discuss as a real product architecture in an interview.

![Architecture overview](assets/architecture-overview.svg)

## System Shape

The system is split into five main areas:

- `backend/api/` for HTTP routes
- `backend/ingestion/` for parsing, cleaning, chunking, and indexing
- `backend/retrieval/` for vector retrieval, lexical fallback, and reranking
- `backend/services.py` for orchestration, confidence, and workflow logic
- `frontend-react/` for the recruiter-facing demo UI

## Request Flow

### Ask flow

1. `/query` receives the question and optional retrieval filters.
2. Retrieval returns a candidate set from Qdrant or the in-memory fallback.
3. `QueryService` narrows the evidence set before generation.
4. The LLM provider generates the answer.
5. Display sources are filtered again to keep the UI focused.
6. Confidence, evidence summary, caution message, and history are recorded.

### Summary flow

1. `/documents/{id}/summary` loads the document chunks.
2. The service builds a summary prompt from bounded document context.
3. The response is returned with sections and source excerpts.

### Compare flow

1. `/query/compare` constrains retrieval to each chosen document.
2. The service builds a comparison-oriented prompt.
3. The frontend receives structured sections and supporting excerpts.

### Synthesis flow

1. `/query/synthesize` constrains retrieval to the selected document set.
2. The service narrows to the most relevant cross-document evidence.
3. The output highlights documents synthesized, cross-document insights, and source highlights.

## Ingestion Pipeline

The ingestion pipeline currently handles `PDF`, `DOCX`, `TXT`, `MD`, and `CSV`.

Flow:

1. save uploaded file to local storage
2. parse file into normalized pages
3. clean the extracted text
4. chunk the text for retrieval
5. persist document and chunk records in SQLite
6. upsert vectors into Qdrant or the in-memory vector store

## Confidence And Evidence

The product is intentionally opinionated about explainability:

- every query response includes a confidence label and score
- the API now exposes `evidence_documents`, `evidence_summary`, and `caution`
- the React UI surfaces the answer, confidence reason, caution, and supporting excerpts in one place

This keeps the demo honest when evidence is thin or spread across multiple sources.

## Runtime Modes

### OpenAI + Qdrant

Best for live demos because it approximates a more production-grade path.

### Local fallback

Useful for tests, local validation, and environments without external services. The fallback path remains deliberate rather than hidden so the repo can still be exercised end to end.

## Persistence

SQLite stores:

- documents
- chunks
- query history
- feedback
- document metadata such as tags, category, date, versioning fields

## Frontend Positioning

The React frontend is the primary portfolio surface. It emphasizes:

- fast scenario loading
- visible proof around each answer
- document management and versioning
- history and feedback traceability

The Streamlit frontend remains available as a lighter secondary surface for dev and fallback use.
