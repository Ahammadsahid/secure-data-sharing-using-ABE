#!/usr/bin/env python3
"""Regenerate local demo state (users.db + encrypted blobs).

This is useful if you want the project to work immediately for a presentation
without manually uploading files first.

It will:
- Delete existing users.db (if present)
- Clear backend/storage/encrypted_files/*
- Recreate tables + seed default users via backend.main
- Insert a few demo SecureFile rows + encrypted blobs

Note: Blockchain approvals still require Ganache + a deployed contract.
"""

from __future__ import annotations

import base64
import json
import os
import sys
from pathlib import Path


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def main() -> None:
    root = _repo_root()
    os.chdir(root)

    # Ensure the repo root is importable (so `import backend` works).
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    # Ensure backend uses the root users.db
    os.environ.pop("SECURE_DATA_SHARING_DB_PATH", None)

    db_path = root / "users.db"
    encrypted_dir = root / "backend" / "storage" / "encrypted_files"

    if db_path.exists():
        db_path.unlink()

    encrypted_dir.mkdir(parents=True, exist_ok=True)
    for p in encrypted_dir.iterdir():
        if p.is_file():
            p.unlink()

    # Importing backend.main creates tables + seeds test users.
    from backend.main import app  # noqa: F401

    from backend.database import SessionLocal
    from backend.models import SecureFile
    from backend.aes.aes_utils import generate_aes_key, encrypt_file
    from backend.abe.cpabe_utils import encrypt_aes_key
    from backend.storage.file_storage import save_encrypted_file

    demo_files = [
        {
            "filename": "confidential_it_file.txt",
            "owner": "admin",
            "policy": "(role:admin OR role:manager) AND (dept:IT) AND clearance:high",
            "content": b"Confidential IT document. High clearance required.\n",
        },
        {
            "filename": "finance_report_q1.txt",
            "owner": "admin",
            "policy": "(role:admin OR role:accountant) AND (dept:Finance) AND clearance:medium",
            "content": b"Finance report Q1. Medium clearance required.\n",
        },
    ]

    db = SessionLocal()
    try:
        for item in demo_files:
            aes_key = generate_aes_key()
            iv, encrypted_data = encrypt_file(item["content"], aes_key)
            file_path = save_encrypted_file(iv + encrypted_data)

            encrypted_key_struct = encrypt_aes_key(aes_key, item["policy"])
            encrypted_key_payload = json.dumps(
                {
                    "encrypted_key": (
                        encrypted_key_struct["encrypted_key"].decode()
                        if hasattr(encrypted_key_struct["encrypted_key"], "decode")
                        else base64.b64encode(encrypted_key_struct["encrypted_key"]).decode()
                    ),
                    "policy": encrypted_key_struct["policy"],
                    "fernet_key": (
                        encrypted_key_struct["fernet_key"].decode()
                        if hasattr(encrypted_key_struct["fernet_key"], "decode")
                        else base64.b64encode(encrypted_key_struct["fernet_key"]).decode()
                    ),
                }
            ).encode()

            secure_file = SecureFile(
                filename=item["filename"],
                owner=item["owner"],
                file_path=file_path,
                encrypted_key=encrypted_key_payload,
                policy=item["policy"],
            )
            db.add(secure_file)

        db.commit()

        print("✅ Demo DB + encrypted files regenerated")
        print(f"   DB: {db_path}")
        print(f"   Encrypted blobs: {encrypted_dir}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
