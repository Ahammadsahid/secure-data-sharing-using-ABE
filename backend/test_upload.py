from __future__ import annotations

import sys

import requests

BASE_URL = "http://127.0.0.1:8000"


def main() -> int:
    # Login (admin)
    r = requests.post(f"{BASE_URL}/login", json={"username": "admin", "password": "admin123"}, timeout=10)
    print("login:", r.status_code)
    if r.status_code != 200:
        print(r.text)
        return 1

    # Upload multipart
    files = {"file": ("smoke.txt", b"hello upload", "text/plain")}
    data = {
        "policy": "(role:admin) AND (dept:IT) AND (clearance:high)",
        "username": "admin",
    }

    r = requests.post(f"{BASE_URL}/files/upload", files=files, data=data, timeout=60)
    print("upload:", r.status_code)
    print(r.text)
    return 0 if r.status_code == 200 else 2


if __name__ == "__main__":
    raise SystemExit(main())
