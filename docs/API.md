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
