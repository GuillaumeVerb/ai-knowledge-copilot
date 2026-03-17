# AI Knowledge Copilot

AI Knowledge Copilot is a document intelligence demo built to show how a grounded internal knowledge assistant can work end to end: ingestion, chunking, retrieval, structured answers, citations, summaries, comparison workflows, confidence signals, and user feedback.

This repository is positioned as both:

- a portfolio project for applied AI / RAG work
- a foundation for a sellable internal knowledge copilot

## What The Product Does

The app lets a user:

- upload internal documents in `PDF`, `DOCX`, `TXT`, or `MD`
- ask grounded questions over the indexed corpus
- generate structured summaries for a single document
- compare two documents side by side
- synthesize guidance across multiple selected documents
- filter retrieval by document, tag, category, and date range
- reimport a document as a new version
- see confidence labels and explainability hints
- leave `Helpful / Not helpful` feedback on answers

## Why This Project Exists

Teams lose time searching fragmented documentation, asking repeat questions, and relying on the same SMEs for answers that already exist in written form. Traditional search usually returns either too much noise or too little context.

This project demonstrates a more useful pattern:

- retrieval before generation
- citations instead of unsupported answers
- narrow, relevant source selection
- product workflows beyond raw chat

## Current Product State

This repo is currently at a credible V2 stage.

Implemented:

- document upload and parsing
- chunking and indexing
- vector retrieval with lexical fallback and hybrid merging
- source-grounded answers
- structured summaries
- document comparison
- multi-document synthesis
- confidence score and confidence reason
- user feedback capture
- metadata filters for `tag`, `category`, `date`
- reimport/versioning flow
- query history
- React frontend for portfolio/demo use
- Streamlit frontend kept as a secondary demo surface

Not implemented yet:

- authentication
- workspaces
- permissions
- external connectors
- analytics dashboards
- public deployment configuration in-repo

## Recommended Frontend

Use the React frontend for portfolio/demo quality.

- React demo: `frontend-react`
- Streamlit demo: `frontend`

Streamlit is still useful for quick local validation, but the React app is the better presentation layer.

## Stack

- Backend: FastAPI, Pydantic, SQLite
- Retrieval: Qdrant or in-memory fallback
- Embeddings / generation: OpenAI or local fallback mode
- Frontends: React + Vite, plus Streamlit
- Testing: pytest
- Dev scripts: shell scripts for demo startup and seeding

## Runtime Modes

### Recommended demo mode

- `OpenAI + Qdrant`

Best answer quality, strongest demo value, and better retrieval behavior.

### Local fallback mode

- stubbed local generation
- in-memory retrieval fallback

Useful for development and testing, but not the best client-facing demo mode.

## Main Workflows

### 1. Ask A Question

The user asks a natural-language question.

The backend:

1. retrieves candidate chunks
2. merges semantic and lexical signals
3. narrows the final context
4. generates a grounded answer
5. filters displayed sources to the most relevant evidence
6. computes a confidence label and stores history

### 2. Summarize One Document

The user selects one document and asks for a structured summary.

The backend returns:

- overview
- key points
- supporting sources

### 3. Compare Two Documents

The user selects a left and right document.

The backend returns structured sections for:

- summary
- points in common
- differences
- operational implications

### 4. Synthesize Multiple Documents

The user selects multiple documents and asks for a cross-document synthesis.

The backend returns:

- overview
- documents synthesized
- cross-document insights
- source highlights

### 5. Reimport A New Version

The user uploads a new version of an existing document.

The backend:

- keeps a shared version group
- increments the version number
- links the new record to the superseded one
- preserves a cleaner history of document evolution

## Quick Start

### 1. Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

### 2. Start the backend

```bash
PYTHONPATH=. .venv/bin/uvicorn backend.main:app --reload --host 127.0.0.1 --port 8010
```

### 3. Start the React frontend

```bash
cd frontend-react
npm install
npm run dev
```

Expected URLs:

- Backend API: `http://localhost:8010`
- React frontend: `http://localhost:5173`

### 4. Optional Streamlit frontend

```bash
API_BASE_URL=http://localhost:8010 .venv/bin/streamlit run frontend/app.py --server.port 8502
```

### 5. Demo helper script

For the original backend + Streamlit flow:

```bash
./scripts/start_demo.sh
```

This script starts:

- backend on `8010`
- Streamlit on `8502`
- demo seeding/reindex flow

## API Surface

### Health and admin

- `GET /health`
- `POST /reindex`
- `POST /demo/seed`

### Documents

- `GET /documents`
- `POST /documents/upload`
- `POST /documents/{id}/reimport`
- `DELETE /documents/{id}`
- `POST /documents/{id}/summary`

Supported `GET /documents` filters:

- `tag`
- `status`
- `search`
- `category`
- `date_from`
- `date_to`
- `include_superseded`

### Querying

- `POST /query`
- `POST /query/compare`
- `POST /query/synthesize`

### History

- `GET /history`
- `POST /history/{id}/feedback`

## Example Portfolio Demo Flow

1. Seed the demo dataset
2. Show the document library with categories, versions, and filters
3. Ask: `What is the remote work policy?`
4. Show the concise answer, confidence badge, and source evidence
5. Summarize an HR or security document
6. Compare `product_guide.md` with `support_procedure.txt`
7. Synthesize guidance across multiple documents
8. Reimport a document as a new version
9. Show the saved history and feedback loop

## Visual Assets

Add real screenshots or a short GIF here to make the portfolio presentation much stronger.

Recommended files:

- `docs/assets/react-dashboard.png`
- `docs/assets/grounded-answer.png`
- `docs/assets/structured-summary.png`
- `docs/assets/document-comparison.png`
- `docs/assets/demo-flow.gif`

Suggested captures:

- React dashboard with indexed documents and filters
- grounded answer with confidence badge and one relevant source
- structured single-document summary
- comparison view with similarities and differences
- short end-to-end GIF: ask -> summarize -> compare -> reimport

Suggested markdown once assets are added:

```md
![Dashboard](docs/assets/react-dashboard.png)
![Grounded answer](docs/assets/grounded-answer.png)
![Structured summary](docs/assets/structured-summary.png)
![Comparison](docs/assets/document-comparison.png)
```

## Documentation

More focused docs live in [`docs/architecture.md`](/Users/guillaumeverbiguie/Desktop/AI knowledge copilot/docs/architecture.md), [`docs/demo-guide.md`](/Users/guillaumeverbiguie/Desktop/AI knowledge copilot/docs/demo-guide.md), [`docs/api-examples.md`](/Users/guillaumeverbiguie/Desktop/AI knowledge copilot/docs/api-examples.md), and [`docs/roadmap.md`](/Users/guillaumeverbiguie/Desktop/AI knowledge copilot/docs/roadmap.md).

## Testing

```bash
PYTHONPATH=. .venv/bin/pytest -q
```

## What This Repo Proves

- end-to-end RAG workflow design
- FastAPI backend architecture
- retrieval quality thinking beyond raw embeddings
- source-aware outputs
- confidence and feedback instrumentation
- product-minded workflow design
- ability to move from quick demo UI to stronger frontend presentation

## Known Limits

- fallback mode is intentionally less impressive than OpenAI mode
- the React frontend is stronger than the Streamlit frontend, but still not a full production design system
- there is no auth or tenant isolation yet
- there are no external document connectors yet

## Recommended Next Steps

- add screenshots and a short GIF to this README
- deploy a public demo
- add auth/workspaces
- add connector ingestion
- add analytics around unanswered or poorly rated questions
