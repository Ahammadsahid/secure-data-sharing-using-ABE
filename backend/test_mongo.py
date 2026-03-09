from __future__ import annotations

import os
import sys
from pathlib import Path

from dotenv import load_dotenv


def _load_env() -> None:
    # Make the script work no matter where it's run from.
    project_root = Path(__file__).resolve().parents[1]
    # If executed as a file path (e.g. python backend/test_mongo.py), Python adds
    # `backend/` to sys.path[0], which breaks `import backend.*`. Ensure the
    # project root is importable.
    sys.path.insert(0, str(project_root))
    load_dotenv(project_root / ".env")


def _mask_uri(uri: str) -> str:
    # Avoid printing secrets.
    # mongodb+srv://user:pass@host/... -> mongodb+srv://user:***@host/...
    if not uri:
        return uri
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

    uri = os.getenv("MONGODB_URI")
    if not uri:
        print("ERROR: MONGODB_URI is not set in .env")
        return 2

    try:
        from backend.mongo_client import get_mongo_client, ping_mongo

        client = get_mongo_client(uri)
        ping_mongo(client)
        print("MongoDB connected successfully!")
        return 0
    except Exception as e:
        print("ERROR: MongoDB connection failed")
        print(f"URI (masked): {_mask_uri(uri)}")
        print(f"Details: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
