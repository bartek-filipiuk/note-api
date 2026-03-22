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
