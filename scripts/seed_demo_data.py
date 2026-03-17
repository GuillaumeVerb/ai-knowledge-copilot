from __future__ import annotations

import argparse
import json
import mimetypes

import requests
from backend.core.dependencies import get_documents_repository, get_ingestion_service
from backend.core.settings import get_settings


DEFAULT_TAGS = {
    "hr_handbook.txt": ["hr", "policy", "onboarding"],
    "product_guide.md": ["product", "support"],
    "support_procedure.txt": ["support", "operations"],
    "internal_policy.txt": ["security", "policy"],
    "quarterly_report.txt": ["reporting", "analytics"],
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-base-url")
    args = parser.parse_args()

    if args.api_base_url:
        seed_via_api(args.api_base_url.rstrip("/"))
        return

    settings = get_settings()
    repository = get_documents_repository()
    ingestion_service = get_ingestion_service()

    existing_names = {document.original_filename for document in repository.list_documents()}
    seeded = 0
    skipped = 0

    for path in sorted(settings.demo_data_dir.iterdir()):
        if not path.is_file():
            continue
        if path.name in existing_names:
            skipped += 1
            print(f"Skipping existing demo document: {path.name}")
            continue

        mime_type, _ = mimetypes.guess_type(str(path))
        result = ingestion_service.ingest_upload(
            filename=path.name,
            mime_type=mime_type or "text/plain",
            content=path.read_bytes(),
            tags=DEFAULT_TAGS.get(path.name, ["demo"]),
        )
        seeded += 1
        print(f"Seeded {result.document.original_filename} ({result.chunks_indexed} chunks)")

    print(f"Done. Seeded={seeded}, skipped={skipped}")


def seed_via_api(api_base_url: str) -> None:
    settings = get_settings()
    response = requests.get(f"{api_base_url}/documents", timeout=60)
    response.raise_for_status()
    existing_names = {document["original_filename"] for document in response.json()}

    seeded = 0
    skipped = 0
    for path in sorted(settings.demo_data_dir.iterdir()):
        if not path.is_file():
            continue
        if path.name in existing_names:
            skipped += 1
            print(f"Skipping existing demo document: {path.name}")
            continue

        mime_type, _ = mimetypes.guess_type(str(path))
        with path.open("rb") as file_handle:
            upload_response = requests.post(
                f"{api_base_url}/documents/upload",
                files={"file": (path.name, file_handle, mime_type or "text/plain")},
                data={"tags": json.dumps(DEFAULT_TAGS.get(path.name, ["demo"]))},
                timeout=120,
            )
        upload_response.raise_for_status()
        payload = upload_response.json()
        seeded += 1
        print(f"Seeded {path.name} ({payload['chunks_indexed']} chunks)")

    print(f"Done. Seeded={seeded}, skipped={skipped}")


if __name__ == "__main__":
    main()
