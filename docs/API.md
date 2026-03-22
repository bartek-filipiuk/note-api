# API Documentation — Notes API

## Health

### GET /health
Sprawdza czy API działa.

**Response:** `200 OK`
```json
{"status": "ok"}
```

---

## Auth

### POST /auth/register
Rejestracja nowego użytkownika. Rate limit: 5 req/min per IP.

**Request body:**
```json
{"email": "user@example.com", "password": "min8chars"}
```

**Walidacja:** email w formacie EmailStr, hasło min. 8 znaków.

**Response:** `201 Created`
```json
{"access_token": "eyJ...", "token_type": "bearer"}
```

**Błędy:** `409` duplikat email, `422` walidacja, `429` rate limit.

### POST /auth/login
Logowanie. Rate limit: 5 req/min per IP.

**Request body:**
```json
{"email": "user@example.com", "password": "password123"}
```

**Response:** `200 OK`
```json
{"access_token": "eyJ...", "token_type": "bearer"}
```

**Błędy:** `401` błędne dane, `429` rate limit.

### GET /auth/whoami
Dane zalogowanego użytkownika.

**Headers:** `Authorization: Bearer <token>`

**Response:** `200 OK`
```json
{"id": 1, "email": "user@example.com", "is_admin": false}
```

**Błędy:** `401` brak/nieprawidłowy/wygasły token.

---

## Notes

Wszystkie endpointy wymagają `Authorization: Bearer <token>`.

### POST /notes
Tworzenie notatki.

**Request body:**
```json
{"title": "Tytuł", "content": "Treść", "tags": ["tag1", "tag2"], "is_public": false}
```

**Response:** `201 Created` — obiekt notatki.

### GET /notes
Lista własnych notatek (+ udostępnionych i publicznych po implementacji sharing).

**Response:** `200 OK` — lista notatek.

### GET /notes/{id}
Szczegóły notatki. Dostęp: właściciel, odbiorca share, lub publiczna.

**Response:** `200 OK` — obiekt notatki.

**Błędy:** `403` brak dostępu, `404` nie znaleziono.

### PUT /notes/{id}
Edycja notatki. Tylko właściciel.

**Request body:** Częściowy update (title, content, tags, is_public — dowolne pola).

**Response:** `200 OK` — zaktualizowana notatka.

**Błędy:** `403` nie właściciel, `404` nie znaleziono.

### DELETE /notes/{id}
Usuwanie notatki. Tylko właściciel.

**Response:** `204 No Content`.

**Błędy:** `403` nie właściciel, `404` nie znaleziono.

### GET /notes?tag={tag}
Filtrowanie notatek po tagu. Zwraca własne + udostępnione + publiczne.

**Query params:** `tag` — nazwa tagu.

**Response:** `200 OK` — lista notatek z danym tagiem.

### POST /notes/{id}/share
Udostępnienie notatki użytkownikowi. Tylko właściciel.

**Request body:**
```json
{"user_id": 2}
```

**Response:** `201 Created`.

**Błędy:** `403` nie właściciel, `404` nota/user nie znaleziony.

### DELETE /notes/{id}/share/{user_id}
Cofnięcie udostępnienia. Tylko właściciel.

**Response:** `204 No Content`.

**Błędy:** `403` nie właściciel, `404` share nie znaleziony.

---

## Attachments

### POST /notes/{id}/attachments
Upload obrazka do notatki (multipart/form-data). Tylko właściciel.

**Dozwolone typy:** JPEG, PNG, GIF, WebP. Max 100 MB.

**Response:** `201 Created` — obiekt attachment.

**Błędy:** `400` niedozwolony typ, `403` nie właściciel, `413` za duży plik.

### GET /notes/{id}/attachments
Lista załączników notatki.

**Response:** `200 OK` — lista attachmentów.

### GET /notes/{id}/attachments/{att_id}
Pobranie pliku załącznika.

**Response:** `200 OK` — plik binarny z Content-Disposition.

### DELETE /notes/{id}/attachments/{att_id}
Usunięcie załącznika. Tylko właściciel notatki.

**Response:** `204 No Content`.

---

## Export

### GET /notes/{id}/export
Eksport notatki do pliku `.txt`. Dostęp: właściciel, odbiorca share, publiczna.

**Response:** `200 OK` — plik `.txt` z Content-Disposition attachment.

**Błędy:** `403` brak dostępu, `404` nie znaleziono.

---

## Admin

### GET /admin/users
Lista wszystkich zarejestrowanych użytkowników. Tylko admin (`is_admin=true`).

**Response:** `200 OK`
```json
[{"id": 1, "email": "user@example.com", "is_admin": false, "created_at": "2026-03-22T..."}]
```

**Błędy:** `401` brak tokena, `403` nie admin.
