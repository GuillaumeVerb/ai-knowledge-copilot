# Demo Guide

This guide is tuned for recruiter demos and short architecture walkthroughs.

## Goal

Present the product in less than 5 minutes while proving:

- the UI is polished enough to feel like a product
- the backend is grounded and structured, not generic chat
- the system exposes confidence and evidence honestly

## Recommended Setup

Best mode:

- React frontend
- backend in `OpenAI + Qdrant` mode if credentials are available

Fallback mode:

- React frontend
- backend in local fallback mode

The fallback path is acceptable for interviews, but say explicitly that OpenAI mode is the best quality path.

## Launch

### Backend

```bash
PYTHONPATH=. .venv/bin/uvicorn backend.main:app --reload --host 127.0.0.1 --port 8010
```

### React frontend

```bash
cd frontend-react
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```

### Seed data

```bash
curl -X POST http://127.0.0.1:8010/demo/seed
```

## 5-Minute Script

### 1. Open the dashboard

What to point out:

- runtime mode is visible
- supported file types are visible
- the app is clearly framed as grounded internal knowledge, not generic chat

### 2. Run the grounded question scenario

Suggested question:

`What is the remote work policy?`

What to point out:

- concise answer
- confidence label and score
- caution messaging when evidence is not perfect
- explicit evidence perimeter and source excerpts

### 3. Show comparison

Suggested pair:

- `product_guide.md`
- `support_procedure.txt`

Suggested question:

`Compare incident escalation procedures`

What to point out:

- structured sections
- differences are easy to scan
- the system stays grounded in actual excerpts

### 4. Show synthesis

Suggested prompt:

`Summarize the main operational guidance across these documents`

What to point out:

- cross-document reasoning
- bounded document scope
- source highlights remain visible

### 5. Show versioning and traceability

What to point out:

- upload or reimport as a new version
- show latest vs superseded behavior
- open recent history and feedback capture

## Reference Questions

These are good default questions for live use:

- `What is the remote work policy?`
- `How should a severity one incident be escalated?`
- `What are the key rules for handling sensitive data?`
- `What should new hires receive during onboarding?`

## Demo Talking Points

- This is not just chat over files.
- Retrieval is narrowed before generation.
- Evidence and caution are visible in the product, not hidden in logs.
- The architecture separates ingestion, retrieval, orchestration, and presentation.
- The current scope is intentionally product-shaped, while still small enough to reason about quickly.
