# Evaluation

The repo includes a lightweight demo evaluation harness so the product can be discussed as an engineered system, not only a UI demo.

## What It Checks

For each reference question, the harness verifies:

- the API returns `status=answered`
- at least one grounded source is present
- the expected document appears in the evidence set
- key answer terms appear in the answer or structured sections

## Reference Scenarios

### `remote-work-policy`

- Question: `What is the remote work policy?`
- Expected evidence: `hr_handbook.txt`

### `incident-escalation`

- Question: `How should a severity one incident be escalated?`
- Expected evidence: `product_guide.md`, `support_procedure.txt`

### `security-guidance`

- Question: `What are the key rules for handling sensitive data?`
- Expected evidence: `internal_policy.txt`

### `onboarding`

- Question: `What should new hires receive during onboarding?`
- Expected evidence: `hr_handbook.txt`

## Run Against A Live API

```bash
PYTHONPATH=. .venv/bin/python scripts/evaluate_demo.py --api-base-url http://127.0.0.1:8010
```

## How To Interpret Results

- all scenarios pass: the demo dataset is coherent and the main recruiter paths are healthy
- some scenarios fail: inspect whether retrieval, answer wording, or source selection regressed

This is intentionally lightweight. It is not a full offline RAG benchmark, but it gives a concrete engineering artifact to discuss in an interview.
