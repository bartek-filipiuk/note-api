def _register_and_get_token(client, email="test@example.com"):
    res = client.post("/auth/register", json={"email": email, "password": "securepass123"})
    return res.json()["access_token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_export_own_note(client):
    token = _register_and_get_token(client)
    create = client.post(
        "/notes",
        json={"title": "My Note", "content": "Hello world", "tags": ["test", "export"]},
        headers=_auth_header(token),
    )
    note_id = create.json()["id"]
    response = client.get(f"/notes/{note_id}/export", headers=_auth_header(token))
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    assert "attachment" in response.headers.get("content-disposition", "")
    text = response.text
    assert "My Note" in text
    assert "Hello world" in text
    assert "test" in text


def test_export_other_user_private_note_forbidden(client):
    token1 = _register_and_get_token(client, "owner@example.com")
    token2 = _register_and_get_token(client, "other@example.com")
    create = client.post(
        "/notes",
        json={"title": "Private", "content": "Secret"},
        headers=_auth_header(token1),
    )
    note_id = create.json()["id"]
    response = client.get(f"/notes/{note_id}/export", headers=_auth_header(token2))
    assert response.status_code == 403
