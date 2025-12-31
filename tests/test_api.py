import requests

BASE_URL = "http://127.0.0.1:8000"

def test_register_login():
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
