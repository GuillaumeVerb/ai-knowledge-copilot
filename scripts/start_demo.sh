#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [[ ! -d ".venv" ]]; then
  echo "Virtualenv .venv not found. Create it first with: python3 -m venv .venv && .venv/bin/pip install -r requirements.txt"
  exit 1
fi

if [[ ! -f ".env" ]]; then
  cp .env.example .env
fi

mkdir -p .run

BACKEND_PORT="${BACKEND_PORT:-8010}"
FRONTEND_PORT="${FRONTEND_PORT:-8502}"
BACKEND_URL="http://localhost:${BACKEND_PORT}"
FRONTEND_URL="http://localhost:${FRONTEND_PORT}"

echo "Starting backend on ${BACKEND_URL}"
nohup env PYTHONPATH=. .venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port "${BACKEND_PORT}" > .run/backend.log 2>&1 < /dev/null &
BACKEND_PID=$!
echo "$BACKEND_PID" > .run/backend.pid

for _ in {1..30}; do
  if curl -fsS "${BACKEND_URL}/health" > /dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo "Reindexing backend state"
curl -fsS -X POST "${BACKEND_URL}/reindex" >> .run/backend.log 2>&1 || true

echo "Seeding demo documents"
PYTHONPATH=. .venv/bin/python scripts/seed_demo_data.py --api-base-url "${BACKEND_URL}" >> .run/backend.log 2>&1 || true

echo "Starting Streamlit on ${FRONTEND_URL}"
nohup env API_BASE_URL="${BACKEND_URL}" .venv/bin/streamlit run frontend/app.py --server.address 0.0.0.0 --server.port "${FRONTEND_PORT}" > .run/frontend.log 2>&1 < /dev/null &
FRONTEND_PID=$!
echo "$FRONTEND_PID" > .run/frontend.pid

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "Logs: .run/backend.log and .run/frontend.log"
