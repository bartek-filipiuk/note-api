# Changelog — Notes API

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
