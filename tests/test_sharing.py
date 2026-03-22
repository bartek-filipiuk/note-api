def _register_and_get_token(client, email="test@example.com"):
    res = client.post("/auth/register", json={"email": email, "password": "securepass123"})
    return res.json()["access_token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def _get_user_id(client, token):
    return client.get("/auth/whoami", headers=_auth_header(token)).json()["id"]


# --- Tag search ---

def test_search_notes_by_tag(client):
    token = _register_and_get_token(client)
    client.post("/notes", json={"title": "A", "content": "x", "tags": ["python", "api"]}, headers=_auth_header(token))
    client.post("/notes", json={"title": "B", "content": "y", "tags": ["rust"]}, headers=_auth_header(token))
    response = client.get("/notes?tag=python", headers=_auth_header(token))
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "A"


def test_search_notes_by_tag_no_results(client):
    token = _register_and_get_token(client)
    client.post("/notes", json={"title": "A", "content": "x", "tags": ["python"]}, headers=_auth_header(token))
    response = client.get("/notes?tag=java", headers=_auth_header(token))
    assert response.status_code == 200
    assert len(response.json()) == 0


# --- Sharing ---

def test_share_note_with_user(client):
    token1 = _register_and_get_token(client, "owner@example.com")
    token2 = _register_and_get_token(client, "reader@example.com")
    user2_id = _get_user_id(client, token2)
    create = client.post("/notes", json={"title": "Shared", "content": "x"}, headers=_auth_header(token1))
    note_id = create.json()["id"]
    # Share
    response = client.post(f"/notes/{note_id}/share", json={"user_id": user2_id}, headers=_auth_header(token1))
    assert response.status_code == 201
    # Reader can access
    response = client.get(f"/notes/{note_id}", headers=_auth_header(token2))
    assert response.status_code == 200
    assert response.json()["title"] == "Shared"


def test_shared_note_appears_in_list(client):
    token1 = _register_and_get_token(client, "owner@example.com")
    token2 = _register_and_get_token(client, "reader@example.com")
    user2_id = _get_user_id(client, token2)
    create = client.post("/notes", json={"title": "Shared", "content": "x"}, headers=_auth_header(token1))
    note_id = create.json()["id"]
    client.post(f"/notes/{note_id}/share", json={"user_id": user2_id}, headers=_auth_header(token1))
    response = client.get("/notes", headers=_auth_header(token2))
    assert response.status_code == 200
    titles = [n["title"] for n in response.json()]
    assert "Shared" in titles


def test_share_note_non_owner_forbidden(client):
    token1 = _register_and_get_token(client, "owner@example.com")
    token2 = _register_and_get_token(client, "other@example.com")
    token3 = _register_and_get_token(client, "third@example.com")
    user3_id = _get_user_id(client, token3)
    create = client.post("/notes", json={"title": "Note", "content": "x"}, headers=_auth_header(token1))
    note_id = create.json()["id"]
    response = client.post(f"/notes/{note_id}/share", json={"user_id": user3_id}, headers=_auth_header(token2))
    assert response.status_code == 403


def test_share_note_nonexistent_user(client):
    token = _register_and_get_token(client)
    create = client.post("/notes", json={"title": "Note", "content": "x"}, headers=_auth_header(token))
    note_id = create.json()["id"]
    response = client.post(f"/notes/{note_id}/share", json={"user_id": 9999}, headers=_auth_header(token))
    assert response.status_code == 404


def test_unshare_note(client):
    token1 = _register_and_get_token(client, "owner@example.com")
    token2 = _register_and_get_token(client, "reader@example.com")
    user2_id = _get_user_id(client, token2)
    create = client.post("/notes", json={"title": "Shared", "content": "x"}, headers=_auth_header(token1))
    note_id = create.json()["id"]
    client.post(f"/notes/{note_id}/share", json={"user_id": user2_id}, headers=_auth_header(token1))
    # Unshare
    response = client.delete(f"/notes/{note_id}/share/{user2_id}", headers=_auth_header(token1))
    assert response.status_code == 204
    # Reader can no longer access
    response = client.get(f"/notes/{note_id}", headers=_auth_header(token2))
    assert response.status_code == 403


def test_shared_note_cannot_be_edited_by_reader(client):
    token1 = _register_and_get_token(client, "owner@example.com")
    token2 = _register_and_get_token(client, "reader@example.com")
    user2_id = _get_user_id(client, token2)
    create = client.post("/notes", json={"title": "Shared", "content": "x"}, headers=_auth_header(token1))
    note_id = create.json()["id"]
    client.post(f"/notes/{note_id}/share", json={"user_id": user2_id}, headers=_auth_header(token1))
    response = client.put(f"/notes/{note_id}", json={"title": "Hacked"}, headers=_auth_header(token2))
    assert response.status_code == 403


def test_shared_note_cannot_be_deleted_by_reader(client):
    token1 = _register_and_get_token(client, "owner@example.com")
    token2 = _register_and_get_token(client, "reader@example.com")
    user2_id = _get_user_id(client, token2)
    create = client.post("/notes", json={"title": "Shared", "content": "x"}, headers=_auth_header(token1))
    note_id = create.json()["id"]
    client.post(f"/notes/{note_id}/share", json={"user_id": user2_id}, headers=_auth_header(token1))
    response = client.delete(f"/notes/{note_id}", headers=_auth_header(token2))
    assert response.status_code == 403
