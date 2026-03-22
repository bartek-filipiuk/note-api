# Changelog — Notes API

## [Stage 5] - 2026-03-22

- Model Attachment (id, note_id, filename, original_filename, mime_type, size_bytes)
- POST /notes/{id}/attachments — upload obrazka (JPEG, PNG, GIF, WebP, max 100 MB)
- GET /notes/{id}/attachments — lista załączników
- GET /notes/{id}/attachments/{att_id} — pobranie pliku
- DELETE /notes/{id}/attachments/{att_id} — usunięcie (tylko właściciel)
- UUID filename sanitization, MIME type validation
- Testy security: upload .exe → 400, upload do cudzej notatki → 403

## [Stage 4] - 2026-03-22

- GET /notes?tag=nazwa — filtrowanie notatek po tagu
- Model NoteShare (udostępnianie notatek)
- POST /notes/{id}/share — udostępnienie notatki userowi
- DELETE /notes/{id}/share/{user_id} — cofnięcie udostępnienia
- GET /notes i GET /notes/{id} uwzględniają notatki udostępnione
- Testy security: share cudzej notatki, edycja/usunięcie shared note

## [Stage 3] - 2026-03-22

- Model Note (id, title, content, tags, is_public, owner_id, timestamps)
- POST /notes — tworzenie notatki
- GET /notes — lista własnych notatek
- GET /notes/{id} — szczegóły (własna, publiczna lub udostępniona)
- PUT /notes/{id} — edycja (tylko właściciel)
- DELETE /notes/{id} — usuwanie (tylko właściciel)
- Testy IDOR: edycja/usunięcie/dostęp do cudzej notatki → 403

## [Stage 2] - 2026-03-22

- Model User (id, email, hashed_password, is_admin, created_at)
- POST /auth/register — rejestracja z walidacją, zwrotka JWT
- POST /auth/login — logowanie, zwrotka JWT
- GET /auth/whoami — dane zalogowanego usera
- Hashowanie haseł bcrypt via passlib
- JWT z TTL 30 min
- Rate limiting 5/min na auth endpoints (slowapi)
- Testy security: duplikat email, błędne hasło, brak tokena, wygasły token

## [Stage 1] - 2026-03-22

- Scaffolding projektu: struktura `app/`, `tests/`
- Health endpoint `GET /health`
- Konfiguracja SQLAlchemy + SQLite via pydantic-settings
- Integracja pytest z TestClient i in-memory SQLite
- Dockerfile + docker-compose.yml z healthcheck
- CORS middleware z restrykcyjną allowlistą
- `.env` z sekretami, `.gitignore` chroni `.env`
