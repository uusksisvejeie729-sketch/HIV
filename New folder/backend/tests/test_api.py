"""API tests (SRS §11 Testing Plan)."""
import pytest


@pytest.fixture
def auth_headers(client):
    email = "testuser@example.com"
    client.post("/register", json={"name": "Test User", "email": email, "password": "TestPass123!"})
    res = client.post("/login", json={"email": email, "password": "TestPass123!"})
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_login_aliases(client):
    email = "alias@example.com"
    r = client.post("/register", json={"name": "Alias", "email": email, "password": "AliasPass123!"})
    assert r.status_code == 201
    r2 = client.post("/login", json={"email": email, "password": "AliasPass123!"})
    assert r2.status_code == 200
    assert "access_token" in r2.json()


def test_predict_requires_auth(client):
    r = client.post(
        "/predict",
        json={
            "age": 30,
            "gender": "male",
            "bmi": 24,
            "cd4_count": 500,
            "sti_history": 0,
            "behavioral_score": 1,
        },
    )
    assert r.status_code == 401


def test_predict_and_history(client, auth_headers):
    r = client.post(
        "/predict",
        headers=auth_headers,
        json={
            "age": 35,
            "gender": "female",
            "bmi": 22.5,
            "cd4_count": 400,
            "sti_history": 0,
            "behavioral_score": 2,
        },
    )
    if r.status_code == 500 and "Model not found" in r.text:
        pytest.skip("ML model not trained — run python ml/train.py")
    assert r.status_code == 200
    body = r.json()
    assert body["risk_level"] in ("Low Risk", "Medium Risk", "High Risk")
    assert "confidence_score" in body
    assert "recommendation" in body

    hist = client.get("/history", headers=auth_headers)
    assert hist.status_code == 200
    assert isinstance(hist.json(), list)


def test_analytics(client, auth_headers):
    r = client.get("/analytics", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "prediction_distribution" in data
    assert "model_metrics" in data


def test_admin_forbidden_for_user(client, auth_headers):
    r = client.get("/admin/users", headers=auth_headers)
    assert r.status_code == 403
