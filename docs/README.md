# Notes API

## Opis

Prosty, bezpieczny REST API do zarządzania prywatnymi notatkami tekstowymi. Użytkownicy mogą się rejestrować, logować, tworzyć notatki z tagami, udostępniać je innym użytkownikom (read-only) oraz załączać obrazki. API obsługuje eksport notatek do pliku `.txt` i posiada endpoint administracyjny do listowania userów.

## Quick Start

```bash
# Klonuj repo
git clone <repo-url>
cd notes-api

# Utwórz .env
cp .env .env.example  # edytuj SECRET_KEY na losowy string

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

API dostępne pod `http://localhost:8000`. Dokumentacja Swagger: `http://localhost:8000/docs`.

## Struktura katalogów

```
notes-api/
├── app/
│   ├── __init__.py
│   ├── main.py          # FastAPI app, middleware, CORS
│   ├── config.py         # Settings z .env (pydantic-settings)
│   └── database.py       # SQLAlchemy engine, session, Base
├── tests/
│   ├── __init__.py
│   ├── conftest.py       # Fixtures (test client, test DB)
│   ├── test_health.py
│   └── test_cors.py
├── docs/
│   ├── README.md
│   ├── API.md
│   └── CHANGELOG.md
├── .env
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
