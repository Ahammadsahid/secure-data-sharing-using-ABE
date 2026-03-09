from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def _load_env() -> None:
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))
    load_dotenv(project_root / ".env")


def _mask_uri(uri: str) -> str:
    if not uri:
        return ""
    try:
        scheme, rest = uri.split("://", 1)
        if "@" not in rest:
            return f"{scheme}://***"
        creds, tail = rest.split("@", 1)
        if ":" in creds:
            user, _pw = creds.split(":", 1)
            return f"{scheme}://{user}:***@{tail}"
        return f"{scheme}://***@{tail}"
    except Exception:
        return "***"


def main() -> int:
    _load_env()

    uri = (os.getenv("MONGODB_URI") or "").strip()
    db_name = (os.getenv("MONGODB_DB") or "secure_data_sharing").strip()
    bucket = (os.getenv("MONGODB_FILES_BUCKET") or "encrypted_files").strip()

    print("MongoDB config:")
    print("- MONGODB_URI (masked):", _mask_uri(uri))
    print("- MONGODB_DB:", db_name)
    print("- MONGODB_FILES_BUCKET:", bucket)

    if not uri:
        print("\nERROR: MONGODB_URI is not set in .env")
        return 2

    try:
        from backend.mongo_client import get_mongo_client

        client = get_mongo_client(uri)
        db = client[db_name]

        files_coll = db[f"{bucket}.files"]
        count = files_coll.count_documents({})
        print(f"\nGridFS bucket summary: {count} file(s) in {db_name}.{bucket}.files")

        print("\nLatest 10 GridFS file entries:")
        for doc in files_coll.find({}, {"filename": 1, "length": 1, "uploadDate": 1, "metadata": 1}).sort(
            "uploadDate", -1
        ).limit(10):
            meta = doc.get("metadata") or {}
            print(
                f"- _id={doc.get('_id')} filename={doc.get('filename')} bytes={doc.get('length')} "
                f"uploadDate={doc.get('uploadDate')} metadata.owner={meta.get('owner')} metadata.policy={meta.get('policy')}"
            )

        return 0
    except Exception as exc:
        print("\nERROR: Could not connect/list GridFS uploads")
        print("Details:", exc)
        print(
            "\nNote: If Atlas TLS is failing on your network, uploads may be falling back to local storage. "
            "Check the SQLite secure_files.file_path value: 'gridfs:<id>' means MongoDB, 'local:<id>' means local fallback."
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
