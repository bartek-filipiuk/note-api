def _register_and_get_token(client, email="test@example.com"):
    res = client.post("/auth/register", json={"email": email, "password": "securepass123"})
    return res.json()["access_token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_note(client):
    token = _register_and_get_token(client)
    response = client.post(
        "/notes",
        json={"title": "My Note", "content": "Hello world", "tags": ["test"], "is_public": False},
        headers=_auth_header(token),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Note"
    assert data["content"] == "Hello world"
    assert data["tags"] == ["test"]
    assert data["is_public"] is False
    assert "id" in data


def test_create_note_unauthenticated(client):
    response = client.post(
        "/notes",
        json={"title": "My Note", "content": "Hello"},
    )
    assert response.status_code == 401


def test_list_own_notes(client):
    token = _register_and_get_token(client)
    client.post("/notes", json={"title": "Note 1", "content": "A"}, headers=_auth_header(token))
    client.post("/notes", json={"title": "Note 2", "content": "B"}, headers=_auth_header(token))
    response = client.get("/notes", headers=_auth_header(token))
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_notes_excludes_others_private(client):
    token1 = _register_and_get_token(client, "user1@example.com")
    token2 = _register_and_get_token(client, "user2@example.com")
    client.post("/notes", json={"title": "Private", "content": "Secret"}, headers=_auth_header(token1))
    response = client.get("/notes", headers=_auth_header(token2))
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_own_note(client):
    token = _register_and_get_token(client)
    create = client.post("/notes", json={"title": "My Note", "content": "X"}, headers=_auth_header(token))
    note_id = create.json()["id"]
    response = client.get(f"/notes/{note_id}", headers=_auth_header(token))
    assert response.status_code == 200
    assert response.json()["title"] == "My Note"


def test_get_other_user_private_note_forbidden(client):
    token1 = _register_and_get_token(client, "user1@example.com")
    token2 = _register_and_get_token(client, "user2@example.com")
    create = client.post("/notes", json={"title": "Private", "content": "X"}, headers=_auth_header(token1))
    note_id = create.json()["id"]
    response = client.get(f"/notes/{note_id}", headers=_auth_header(token2))
    assert response.status_code == 403


def test_get_public_note_by_other_user(client):
    token1 = _register_and_get_token(client, "user1@example.com")
    token2 = _register_and_get_token(client, "user2@example.com")
    create = client.post(
        "/notes",
        json={"title": "Public", "content": "X", "is_public": True},
        headers=_auth_header(token1),
    )
    note_id = create.json()["id"]
    response = client.get(f"/notes/{note_id}", headers=_auth_header(token2))
    assert response.status_code == 200


def test_update_own_note(client):
    token = _register_and_get_token(client)
    create = client.post("/notes", json={"title": "Old", "content": "X"}, headers=_auth_header(token))
    note_id = create.json()["id"]
    response = client.put(
        f"/notes/{note_id}",
        json={"title": "New", "content": "Y", "tags": ["updated"]},
        headers=_auth_header(token),
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New"
    assert response.json()["tags"] == ["updated"]


def test_update_other_user_note_forbidden(client):
    token1 = _register_and_get_token(client, "user1@example.com")
    token2 = _register_and_get_token(client, "user2@example.com")
    create = client.post("/notes", json={"title": "Note", "content": "X"}, headers=_auth_header(token1))
    note_id = create.json()["id"]
    response = client.put(
        f"/notes/{note_id}",
        json={"title": "Hacked", "content": "Y"},
        headers=_auth_header(token2),
    )
    assert response.status_code == 403


def test_delete_own_note(client):
    token = _register_and_get_token(client)
    create = client.post("/notes", json={"title": "Delete me", "content": "X"}, headers=_auth_header(token))
    note_id = create.json()["id"]
    response = client.delete(f"/notes/{note_id}", headers=_auth_header(token))
    assert response.status_code == 204
    get_response = client.get(f"/notes/{note_id}", headers=_auth_header(token))
    assert get_response.status_code == 404


def test_delete_other_user_note_forbidden(client):
    token1 = _register_and_get_token(client, "user1@example.com")
    token2 = _register_and_get_token(client, "user2@example.com")
    create = client.post("/notes", json={"title": "Note", "content": "X"}, headers=_auth_header(token1))
    note_id = create.json()["id"]
    response = client.delete(f"/notes/{note_id}", headers=_auth_header(token2))
    assert response.status_code == 403
