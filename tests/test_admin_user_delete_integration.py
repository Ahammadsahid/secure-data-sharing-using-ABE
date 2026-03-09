import pytest
import requests

BASE_URL = "http://127.0.0.1:8000"


def _server_is_up() -> bool:
    try:
        r = requests.get(f"{BASE_URL}/docs", timeout=1)
        return r.status_code in (200, 404)
    except Exception:
        return False


def _basic_auth_headers(username: str, password: str) -> dict:
    import base64

    token = base64.b64encode(f"{username}:{password}".encode("ascii")).decode("ascii")
    return {"Authorization": f"Basic {token}"}


def test_admin_can_delete_user():
    if not _server_is_up():
        pytest.skip("FastAPI server is not running on 127.0.0.1:8000")

    headers = _basic_auth_headers("admin", "admin123")

    # Create a temporary user
    username = "tmp_delete_me"
    payload = {
        "username": username,
        "role": "employee",
        "department": "IT",
        "clearance": "medium",
        "password": "TmpPass12!",
    }
    r = requests.post(f"{BASE_URL}/admin/users", json=payload, headers=headers, timeout=5)
    assert r.status_code in (200, 400)  # 400 if user already exists from a previous run

    # Delete the user
    r = requests.delete(
        f"{BASE_URL}/admin/users/{username}",
        params={"delete_files": "false"},
        headers=headers,
        timeout=10,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["username"] == username
