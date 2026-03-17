#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

for service in backend frontend; do
  PID_FILE=".run/${service}.pid"
  if [[ -f "$PID_FILE" ]]; then
    PID="$(cat "$PID_FILE")"
    if kill "$PID" >/dev/null 2>&1; then
      echo "Stopped $service ($PID)"
    fi
    rm -f "$PID_FILE"
  fi
done
