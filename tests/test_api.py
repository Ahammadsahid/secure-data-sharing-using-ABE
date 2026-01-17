def test_register_login(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient

    # Use an isolated DB for tests (does not touch the repo's local users.db)
    test_db_path = tmp_path / "tests_users.db"
    monkeypatch.setenv("SECURE_DATA_SHARING_DB_PATH", str(test_db_path))

    from backend.main import app

    client = TestClient(app)

    r = client.post(
        "/register",
        json={"username": "testuser9", "password": "testpass", "role": "employee"},
    )
    assert r.status_code == 403

    r = client.post(
        "/login",
        json={"username": "admin", "password": "admin123"},
    )
    assert r.status_code == 200
