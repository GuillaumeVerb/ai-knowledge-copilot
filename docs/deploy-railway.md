# Deploy To Railway

This project is easiest to deploy on Railway as 3 services:

1. `backend`
2. `frontend-react`
3. `qdrant`

The goal is:

- public React frontend
- public FastAPI backend
- private Qdrant service used by the backend

## Architecture

- `frontend-react` calls the public backend URL through `VITE_API_BASE_URL`
- `backend` connects to Qdrant through Railway private networking
- `qdrant` persists vectors and enables `retrieval_mode: "qdrant"`

## Service 1: Qdrant

Create a Railway service from the Docker image:

- image: `qdrant/qdrant:v1.15.1`

Recommended settings:

- internal port: `6333`
- add a persistent volume mounted to `/qdrant/storage`

Use the service's private DNS hostname inside Railway.

Typical internal URL:

`http://qdrant.railway.internal:6333`

## Service 2: Backend

Use the repository root as the service source and set:

- `RAILWAY_DOCKERFILE_PATH=docker/Dockerfile.backend`

Set these environment variables on the backend service:

```env
APP_ENV=production
QDRANT_URL=http://qdrant.railway.internal:6333
QDRANT_COLLECTION_NAME=knowledge_chunks
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
EMBEDDING_MODEL=text-embedding-3-small
```

Optional but useful:

```env
ENABLE_RERANKING=true
RETRIEVAL_TOP_K=6
RETRIEVAL_FETCH_K=12
MAX_SUMMARY_CHUNKS=12
```

After deploy, verify:

- `GET /health`
- expected result includes `retrieval_mode: "qdrant"`
- set Railway healthcheck path to `/health`

Then initialize the vector store:

- `POST /reindex`

If you want demo content in production:

- `POST /demo/seed`

## Service 3: Frontend React

Use the repository root as the service source and set:

- `RAILWAY_DOCKERFILE_PATH=frontend-react/Dockerfile`

Set this environment variable on the frontend service:

```env
VITE_API_BASE_URL=https://your-backend-public-domain
```

The frontend build reads `VITE_API_BASE_URL` at build time, so redeploy the frontend after changing it.

## Validation Checklist

After all 3 services are up:

1. Open the frontend public URL
2. Confirm the runtime badge is connected
3. Check the backend `/health`
4. Confirm `retrieval_mode` is `qdrant`
5. Create or edit an assistant profile in the builder UI
6. Ask a question and verify:
   - answer returned
   - sources visible
   - confidence visible
   - active assistant visible

## Expected Outcome

You should end up with:

- a public builder-style AI product
- visible assistant configuration
- live grounded retrieval
- a demo URL that is credible for portfolio, recruiter, and client conversations
