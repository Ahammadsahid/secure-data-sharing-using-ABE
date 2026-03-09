from __future__ import annotations

from pathlib import Path

from backend.storage.storage_backend import delete_encrypted_blob, load_encrypted_blob


def test_storage_backend_supports_legacy_filesystem_paths(tmp_path: Path) -> None:
    # Some older DB records stored a filesystem path in SecureFile.file_path
    # (e.g. backend/storage/encrypted_files/<uuid>) instead of gridfs:/local: keys.
    legacy_file = tmp_path / "legacy_encrypted_blob.bin"
    payload = b"encrypted-bytes"
    legacy_file.write_bytes(payload)

    assert load_encrypted_blob(str(legacy_file)) == payload

    delete_encrypted_blob(str(legacy_file))
    assert not legacy_file.exists()
