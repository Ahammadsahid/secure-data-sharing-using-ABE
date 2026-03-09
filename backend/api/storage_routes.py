from __future__ import annotations

import os
from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/storage", tags=["Storage"])


def _env_bool(name: str, default: bool = False) -> bool:
    value = (os.getenv(name) or "").strip().lower()
    if not value:
        return default
    return value in {"1", "true", "yes", "y", "on"}


@router.get("/health")
def storage_health() -> dict[str, Any]:
    """Quick runtime check: which backend is configured and is MongoDB reachable."""

    storage_backend = (os.getenv("STORAGE_BACKEND") or "mongo").strip().lower()
    allow_local_fallback = _env_bool("STORAGE_ALLOW_LOCAL_FALLBACK", default=True)

    info: dict[str, Any] = {
        "storage_backend": storage_backend,
        "allow_local_fallback": allow_local_fallback,
        "mongo": {
            "configured": bool((os.getenv("MONGODB_URI") or "").strip()),
            "db": (os.getenv("MONGODB_DB") or "secure_data_sharing").strip(),
            "bucket": (os.getenv("MONGODB_FILES_BUCKET") or "encrypted_files").strip(),
            "reachable": False,
            "error": None,
            "gridfs_files_count": None,
        },
    }

    if not info["mongo"]["configured"]:
        return info

    try:
        from backend.mongo_client import get_mongo_client

        client = get_mongo_client()
        client.admin.command("ping")

        db = client[info["mongo"]["db"]]
        files_coll = db[f"{info['mongo']['bucket']}.files"]
        info["mongo"]["gridfs_files_count"] = files_coll.count_documents({})
        info["mongo"]["reachable"] = True
    except Exception as exc:  # noqa: BLE001 - surfacing error string is intended
        info["mongo"]["error"] = str(exc)

    return info
