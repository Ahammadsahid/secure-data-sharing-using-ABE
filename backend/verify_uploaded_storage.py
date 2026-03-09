from __future__ import annotations

import sys
from pathlib import Path


def main() -> int:
    # Ensure project root importable
    project_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(project_root))

    from backend.database import SessionLocal
    from backend.models import SecureFile

    db = SessionLocal()
    try:
        files = db.query(SecureFile).order_by(SecureFile.id.desc()).limit(20).all()
        if not files:
            print("No SecureFile records found in SQLite.")
            return 0

        print("Latest SecureFile entries (SQLite):")
        for f in files:
            path = f.file_path or ""
            backend = "mongo" if (path.startswith("gridfs:") or len(path) == 24) else "local" if path.startswith("local:") else "unknown"
            print(f"- id={f.id} filename={f.filename} owner={f.owner} storage={backend} file_path={path}")

        print("\nHow to interpret:")
        print("- storage=mongo: file_path starts with 'gridfs:' (or looks like a 24-char ObjectId)")
        print("- storage=local: file_path starts with 'local:'")
        return 0
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
