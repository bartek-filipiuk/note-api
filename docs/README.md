# Notes API

## Opis

Prosty, bezpieczny REST API do zarządzania prywatnymi notatkami tekstowymi. Użytkownicy mogą się rejestrować, logować, tworzyć notatki z tagami, udostępniać je innym użytkownikom (read-only) oraz załączać obrazki. API obsługuje eksport notatek do pliku `.txt` i posiada endpoint administracyjny do listowania userów.

**Tech stack:** FastAPI, SQLAlchemy, SQLite, JWT, bcrypt, slowapi.

## Quick Start

```bash
# Klonuj repo
git clone <repo-url>
cd notes-api

# Utwórz .env (edytuj SECRET_KEY na losowy string!)
cp .env.example .env

# Uruchom z Docker
docker compose up --build

# Lub lokalnie
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Testy
pytest tests/ -v
```

API dostępne pod `http://localhost:8000`.
Dokumentacja Swagger: `http://localhost:8000/docs`.
Dokumentacja ReDoc: `http://localhost:8000/redoc`.

## Struktura katalogów

```
notes-api/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, middleware, CORS, security headers
│   ├── config.py             # Settings z .env (pydantic-settings)
│   ├── database.py           # SQLAlchemy engine, session, Base
│   ├── dependencies.py       # get_current_user (JWT auth)
│   ├── models/
│   │   ├── user.py           # User model
│   │   ├── note.py           # Note model
│   │   ├── note_share.py     # NoteShare model
│   │   └── attachment.py     # Attachment model
│   ├── schemas/
│   │   ├── auth.py           # Pydantic schemas: register, login, token, user
│   │   └── notes.py          # Pydantic schemas: note CRUD
│   ├── services/
│   │   └── auth.py           # JWT, bcrypt, token creation/verification
│   └── routers/
│       ├── auth.py           # /auth/* endpoints
│       ├── notes.py          # /notes/* CRUD + sharing
│       ├── uploads.py        # /notes/{id}/attachments/*
│       ├── export.py         # /notes/{id}/export
│       └── admin.py          # /admin/users
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_cors.py
│   ├── test_auth.py
│   ├── test_notes.py
│   ├── test_sharing.py
│   ├── test_uploads.py
│   ├── test_export.py
│   └── test_admin.py
├── docs/
│   ├── README.md
│   ├── API.md
│   └── CHANGELOG.md
├── uploads/                  # Katalog na uploadowane pliki (w .gitignore)
├── .env                      # Sekrety (w .gitignore)
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Endpointy

| Metoda | Endpoint | Opis | Auth |
|--------|---------|------|------|
| GET | /health | Health check | Nie |
| POST | /auth/register | Rejestracja | Nie |
| POST | /auth/login | Logowanie | Nie |
| GET | /auth/whoami | Dane usera | JWT |
| POST | /notes | Tworzenie notatki | JWT |
| GET | /notes | Lista notatek | JWT |
| GET | /notes/{id} | Szczegóły notatki | JWT |
| PUT | /notes/{id} | Edycja notatki | JWT (owner) |
| DELETE | /notes/{id} | Usuwanie notatki | JWT (owner) |
| GET | /notes?tag=X | Wyszukiwanie po tagu | JWT |
| POST | /notes/{id}/share | Udostępnienie notatki | JWT (owner) |
| DELETE | /notes/{id}/share/{uid} | Cofnięcie share | JWT (owner) |
| POST | /notes/{id}/attachments | Upload obrazka | JWT (owner) |
| GET | /notes/{id}/attachments | Lista załączników | JWT |
| GET | /notes/{id}/attachments/{aid} | Pobranie pliku | JWT |
| DELETE | /notes/{id}/attachments/{aid} | Usunięcie załącznika | JWT (owner) |
| GET | /notes/{id}/export | Eksport do .txt | JWT (access) |
| GET | /admin/users | Lista userów | JWT (admin) |
