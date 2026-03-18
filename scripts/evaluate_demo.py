#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys

import requests

from backend.evaluation import evaluate_query_scenarios, summarize_results


def main() -> int:
    parser = argparse.ArgumentParser(description="Run lightweight demo evaluation scenarios against the API.")
    parser.add_argument("--api-base-url", default="http://127.0.0.1:8010")
    args = parser.parse_args()

    base_url = args.api_base_url.rstrip("/")

    def ask_query(payload: dict) -> dict:
        response = requests.post(f"{base_url}/query", json=payload, timeout=20)
        response.raise_for_status()
        return response.json()

    results = evaluate_query_scenarios(ask_query)
    summary = summarize_results(results)
    print(json.dumps(summary, indent=2))
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
