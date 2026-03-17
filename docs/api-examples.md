# API Examples

## Health

```bash
curl http://127.0.0.1:8010/health
```

Example response:

```json
{
  "status": "ok",
  "llm_mode": "local-fallback",
  "retrieval_mode": "in-memory",
  "recommended_mode": "openai"
}
```

## Upload A Document

```bash
curl -X POST http://127.0.0.1:8010/documents/upload \
  -F 'file=@./data/demo_docs/hr_handbook.txt' \
  -F 'tags=["hr","policy"]' \
  -F 'category=HR' \
  -F 'document_date=2026-01-10'
```

## List Documents With Filters

```bash
curl "http://127.0.0.1:8010/documents?category=HR&date_from=2026-01-01&include_superseded=false"
```

## Ask A Question

```bash
curl -X POST http://127.0.0.1:8010/query \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "What is the remote work policy?",
    "filters": {
      "tags": ["policy"],
      "categories": ["HR"]
    },
    "answer_format": "default",
    "use_reranking": true
  }'
```

Example response shape:

```json
{
  "answer": "Remote work is available up to two days per week...",
  "sources": [],
  "used_context_count": 1,
  "latency_ms": 8,
  "status": "answered",
  "answer_format": "default",
  "sections": [],
  "comparison_mode": false,
  "confidence_label": "high",
  "confidence_score": 0.82,
  "confidence_reason": "Answer supported by 1 concentrated and relevant source(s).",
  "history_id": "..."
}
```

## Compare Two Documents

```bash
curl -X POST http://127.0.0.1:8010/query/compare \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "Compare incident escalation procedures",
    "left_document_id": "DOC_ID_LEFT",
    "right_document_id": "DOC_ID_RIGHT",
    "answer_format": "default"
  }'
```

## Synthesize Multiple Documents

```bash
curl -X POST http://127.0.0.1:8010/query/synthesize \
  -H 'Content-Type: application/json' \
  -d '{
    "question": "Summarize the main operational guidance across these documents",
    "document_ids": ["DOC_ID_1", "DOC_ID_2", "DOC_ID_3"],
    "answer_format": "resume"
  }'
```

## Summarize One Document

```bash
curl -X POST http://127.0.0.1:8010/documents/DOC_ID/summary
```

## Reimport A Document As A New Version

```bash
curl -X POST http://127.0.0.1:8010/documents/DOC_ID/reimport \
  -F 'file=@./updated_policy.txt' \
  -F 'document_date=2026-02-20'
```

## Leave Feedback

```bash
curl -X POST http://127.0.0.1:8010/history/HISTORY_ID/feedback \
  -H 'Content-Type: application/json' \
  -d '{
    "feedback_score": 1,
    "feedback_note": "Useful and concise"
  }'
```

## Reindex

```bash
curl -X POST http://127.0.0.1:8010/reindex
```

## Seed Demo Data

```bash
curl -X POST http://127.0.0.1:8010/demo/seed
```
