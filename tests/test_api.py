import requests

BASE_URL = "http://127.0.0.1:8000"

def test_register_login():
    r = requests.post(
        f"{BASE_URL}/auth/register",
        json={"username": "testuser9", "password": "testpass"}
    )
    assert r.status_code in [200, 400]

    r = requests.post(
        f"{BASE_URL}/auth/login",
        json={"username": "testuser9", "password": "testpass"}
    )
    assert r.status_code == 200

    print("PASS: Frontend ↔ Backend API integration")
