from datetime import datetime, timedelta, timezone

from jose import jwt

from app.config import settings
from app.services.auth import ALGORITHM


def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "securepass123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_register_duplicate_email(client):
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "securepass123"},
    )
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "otherpass123"},
    )
    assert response.status_code == 409


def test_register_invalid_email(client):
    response = client.post(
        "/auth/register",
        json={"email": "not-an-email", "password": "securepass123"},
    )
    assert response.status_code == 422


def test_register_short_password(client):
    response = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "short"},
    )
    assert response.status_code == 422


def test_login_success(client):
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "securepass123"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "securepass123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "securepass123"},
    )
    response = client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "wrongpass123"},
    )
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post(
        "/auth/login",
        json={"email": "nobody@example.com", "password": "securepass123"},
    )
    assert response.status_code == 401


def test_whoami_authenticated(client):
    reg = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "securepass123"},
    )
    token = reg.json()["access_token"]
    response = client.get(
        "/auth/whoami",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "is_admin" in data


def test_whoami_no_token(client):
    response = client.get("/auth/whoami")
    assert response.status_code == 401


def test_whoami_invalid_token(client):
    response = client.get(
        "/auth/whoami",
        headers={"Authorization": "Bearer invalid-token-here"},
    )
    assert response.status_code == 401


def test_whoami_expired_token(client):
    reg = client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "securepass123"},
    )
    user_id = reg.json()["access_token"]
    expired_token = jwt.encode(
        {"sub": "1", "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )
    response = client.get(
        "/auth/whoami",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401
