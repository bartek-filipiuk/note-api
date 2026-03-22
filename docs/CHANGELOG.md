# Changelog — Notes API

## [Stage 1] - 2026-03-22

- Scaffolding projektu: struktura `app/`, `tests/`
- Health endpoint `GET /health`
- Konfiguracja SQLAlchemy + SQLite via pydantic-settings
- Integracja pytest z TestClient i in-memory SQLite
- Dockerfile + docker-compose.yml z healthcheck
- CORS middleware z restrykcyjną allowlistą
- `.env` z sekretami, `.gitignore` chroni `.env`
