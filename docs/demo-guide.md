# Demo Guide

## Goal

This guide is for presenting the app as a portfolio project or client-facing prototype.

Use the React frontend when possible.

## Recommended Setup

### Best quality

- backend with `OPENAI_API_KEY`
- Qdrant available
- React frontend

### Local fallback

- backend without OpenAI
- in-memory retrieval fallback
- still usable for development and testing

## Launch

### Backend

```bash
PYTHONPATH=. .venv/bin/uvicorn backend.main:app --reload --host 127.0.0.1 --port 8010
```

### React frontend

```bash
cd frontend-react
npm install
npm run dev
```

### Seed data

Use the UI button or:

```bash
curl -X POST http://127.0.0.1:8010/demo/seed
```

## Demo Sequence

### 1. Show the document library

What to point out:

- multiple documents are already indexed
- tags, categories, dates, and versions are visible
- filters can narrow the working set

### 2. Ask a grounded question

Suggested question:

`What is the remote work policy?`

What to point out:

- concise answer
- confidence label
- source evidence
- history capture

### 3. Summarize a document

Good candidates:

- HR handbook
- security policy

What to point out:

- single-document scope
- structured sections
- limited supporting sources

### 4. Compare two documents

Suggested pair:

- `product_guide.md`
- `support_procedure.txt`

Suggested prompt:

`Compare incident escalation procedures`

What to point out:

- similarities
- differences
- operational implications

### 5. Synthesize across documents

Select 2 to 3 documents and ask:

`Summarize the main operational guidance across these documents`

What to point out:

- multi-document reasoning
- cross-document highlights
- grounded source excerpts

### 6. Show versioning

Reimport a document as a new version.

What to point out:

- incremented version number
- latest vs superseded view
- filtered list behavior

### 7. Show the feedback loop

Use `Helpful` or `Not helpful`.

What to point out:

- answer quality is instrumented
- the product can later learn from poor responses

## Talking Points

- This is not just chat over files.
- The product supports retrieval controls, source narrowing, confidence, and operational workflows.
- The backend logic is separated from the frontend.
- The app is designed to grow toward SaaS features later.
