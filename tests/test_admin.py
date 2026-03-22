from app.models.user import User


def _register_and_get_token(client, email="test@example.com"):
    res = client.post("/auth/register", json={"email": email, "password": "securepass123"})
    return res.json()["access_token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_admin_list_users(client, db_session):
    token = _register_and_get_token(client)
    # Make user admin
    user = db_session.query(User).first()
    user.is_admin = True
    db_session.commit()
    response = client.get("/admin/users", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "email" in data[0]
    assert "id" in data[0]
    assert "created_at" in data[0]


def test_admin_list_users_non_admin_forbidden(client):
    token = _register_and_get_token(client)
    response = client.get("/admin/users", headers=_auth_header(token))
    assert response.status_code == 403


def test_admin_list_users_no_token(client):
    response = client.get("/admin/users")
    assert response.status_code == 401
