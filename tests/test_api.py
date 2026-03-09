import pytest
import requests

BASE_URL = "http://127.0.0.1:8000"


def _server_is_up() -> bool:
    try:
        r = requests.get(f"{BASE_URL}/docs", timeout=1)
        return r.status_code in (200, 404)
    except Exception:
        return False

def test_register_login():
    if not _server_is_up():
        pytest.skip("FastAPI server is not running on 127.0.0.1:8000")

    r = requests.post(
        f"{BASE_URL}/register",
        json={"username": "testuser9", "password": "testpass", "role": "employee"}
    )
    assert r.status_code == 403

    r = requests.post(
        f"{BASE_URL}/login",
        json={"username": "admin", "password": "admin123"}
    )
    assert r.status_code == 200

    print("PASS: Frontend ↔ Backend API integration")
