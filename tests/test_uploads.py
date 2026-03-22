import io


def _register_and_get_token(client, email="test@example.com"):
    res = client.post("/auth/register", json={"email": email, "password": "securepass123"})
    return res.json()["access_token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def _create_note(client, token):
    res = client.post("/notes", json={"title": "Note", "content": "x"}, headers=_auth_header(token))
    return res.json()["id"]


def _fake_image(name="test.png", content=b"\x89PNG\r\n\x1a\n" + b"\x00" * 100, content_type="image/png"):
    return ("file", (name, io.BytesIO(content), content_type))


def test_upload_image(client):
    token = _register_and_get_token(client)
    note_id = _create_note(client, token)
    response = client.post(
        f"/notes/{note_id}/attachments",
        files=[_fake_image()],
        headers=_auth_header(token),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["original_filename"] == "test.png"
    assert data["mime_type"] == "image/png"


def test_upload_invalid_type(client):
    token = _register_and_get_token(client)
    note_id = _create_note(client, token)
    response = client.post(
        f"/notes/{note_id}/attachments",
        files=[("file", ("malware.exe", io.BytesIO(b"MZ" + b"\x00" * 100), "application/octet-stream"))],
        headers=_auth_header(token),
    )
    assert response.status_code == 400


def test_upload_to_other_user_note_forbidden(client):
    token1 = _register_and_get_token(client, "owner@example.com")
    token2 = _register_and_get_token(client, "other@example.com")
    note_id = _create_note(client, token1)
    response = client.post(
        f"/notes/{note_id}/attachments",
        files=[_fake_image()],
        headers=_auth_header(token2),
    )
    assert response.status_code == 403


def test_list_attachments(client):
    token = _register_and_get_token(client)
    note_id = _create_note(client, token)
    client.post(f"/notes/{note_id}/attachments", files=[_fake_image()], headers=_auth_header(token))
    response = client.get(f"/notes/{note_id}/attachments", headers=_auth_header(token))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_download_attachment(client):
    token = _register_and_get_token(client)
    note_id = _create_note(client, token)
    upload = client.post(f"/notes/{note_id}/attachments", files=[_fake_image()], headers=_auth_header(token))
    att_id = upload.json()["id"]
    response = client.get(f"/notes/{note_id}/attachments/{att_id}", headers=_auth_header(token))
    assert response.status_code == 200


def test_delete_attachment(client):
    token = _register_and_get_token(client)
    note_id = _create_note(client, token)
    upload = client.post(f"/notes/{note_id}/attachments", files=[_fake_image()], headers=_auth_header(token))
    att_id = upload.json()["id"]
    response = client.delete(f"/notes/{note_id}/attachments/{att_id}", headers=_auth_header(token))
    assert response.status_code == 204


def test_delete_attachment_by_non_owner_forbidden(client):
    token1 = _register_and_get_token(client, "owner@example.com")
    token2 = _register_and_get_token(client, "other@example.com")
    note_id = _create_note(client, token1)
    upload = client.post(f"/notes/{note_id}/attachments", files=[_fake_image()], headers=_auth_header(token1))
    att_id = upload.json()["id"]
    response = client.delete(f"/notes/{note_id}/attachments/{att_id}", headers=_auth_header(token2))
    assert response.status_code == 403


# --- IDOR fix tests ---

def test_list_attachments_of_other_user_private_note_forbidden(client):
    token1 = _register_and_get_token(client, "owner@example.com")
    token2 = _register_and_get_token(client, "other@example.com")
    note_id = _create_note(client, token1)
    client.post(f"/notes/{note_id}/attachments", files=[_fake_image()], headers=_auth_header(token1))
    response = client.get(f"/notes/{note_id}/attachments", headers=_auth_header(token2))
    assert response.status_code == 403


def test_download_attachment_of_other_user_private_note_forbidden(client):
    token1 = _register_and_get_token(client, "owner@example.com")
    token2 = _register_and_get_token(client, "other@example.com")
    note_id = _create_note(client, token1)
    upload = client.post(f"/notes/{note_id}/attachments", files=[_fake_image()], headers=_auth_header(token1))
    att_id = upload.json()["id"]
    response = client.get(f"/notes/{note_id}/attachments/{att_id}", headers=_auth_header(token2))
    assert response.status_code == 403


def test_shared_user_can_list_attachments(client):
    token1 = _register_and_get_token(client, "owner@example.com")
    token2 = _register_and_get_token(client, "reader@example.com")
    user2_id = client.get("/auth/whoami", headers=_auth_header(token2)).json()["id"]
    note_id = _create_note(client, token1)
    client.post(f"/notes/{note_id}/share", json={"user_id": user2_id}, headers=_auth_header(token1))
    client.post(f"/notes/{note_id}/attachments", files=[_fake_image()], headers=_auth_header(token1))
    response = client.get(f"/notes/{note_id}/attachments", headers=_auth_header(token2))
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_public_note_attachments_accessible(client):
    token1 = _register_and_get_token(client, "owner@example.com")
    token2 = _register_and_get_token(client, "other@example.com")
    res = client.post(
        "/notes",
        json={"title": "Public", "content": "x", "is_public": True},
        headers=_auth_header(token1),
    )
    note_id = res.json()["id"]
    client.post(f"/notes/{note_id}/attachments", files=[_fake_image()], headers=_auth_header(token1))
    response = client.get(f"/notes/{note_id}/attachments", headers=_auth_header(token2))
    assert response.status_code == 200


# --- MIME spoofing test ---

def test_upload_mime_spoofing_rejected(client):
    token = _register_and_get_token(client)
    note_id = _create_note(client, token)
    exe_content = b"MZ" + b"\x00" * 100  # PE header, not PNG magic bytes
    response = client.post(
        f"/notes/{note_id}/attachments",
        files=[("file", ("evil.png", io.BytesIO(exe_content), "image/png"))],
        headers=_auth_header(token),
    )
    assert response.status_code == 400
