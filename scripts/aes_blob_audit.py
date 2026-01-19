"""Audit encrypted file blobs for AES-GCM vs legacy AES-CBC format.

New format (AES-GCM): b"GCM1" + nonce(12) + ciphertext||tag
Legacy format (AES-CBC): iv(16) + ciphertext

This script does NOT decrypt; it only inspects headers.
"""

from __future__ import annotations

import os


def main() -> None:
    base_dir = os.path.join("backend", "storage", "encrypted_files")
    if not os.path.isdir(base_dir):
        raise SystemExit(f"Encrypted files dir not found: {base_dir}")

    total = 0
    gcm = 0
    legacy = 0
    unknown = 0

    for name in os.listdir(base_dir):
        path = os.path.join(base_dir, name)
        if not os.path.isfile(path):
            continue

        total += 1
        with open(path, "rb") as f:
            header = f.read(4)

        if header == b"GCM1":
            gcm += 1
        else:
            # If it's not GCM1, it's treated as legacy by decrypt_blob.
            # We count it as legacy if it's at least 16 bytes.
            try:
                size = os.path.getsize(path)
            except OSError:
                size = 0
            if size >= 16:
                legacy += 1
            else:
                unknown += 1

    print("AES blob audit")
    print(f"- total   : {total}")
    print(f"- gcm     : {gcm}")
    print(f"- legacy  : {legacy}")
    print(f"- invalid : {unknown}")


if __name__ == "__main__":
    main()
