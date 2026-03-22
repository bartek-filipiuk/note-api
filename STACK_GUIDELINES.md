# Stack Guidelines — Notes API

## Must-have na start

### Standard kodowania
- Python: PEP 8, type hints na publicznych funkcjach i schematach Pydantic.
- Formatowanie: `ruff format` (zastępuje black).
- Linting: `ruff check` z domyślnymi regułami + `I` (import sorting).
- Struktura projektu: modularny podział — `app/auth/`, `app/notes/`, `app/admin/`, `app/uploads/`.

### Testy
- Framework: `pytest` z `httpx.AsyncClient` lub `TestClient`.
- TDD obowiązkowe: test → fail → kod → pass.
- Osobna baza testowa (SQLite in-memory lub plik tymczasowy).
- Testy security (negative cases) w każdym module.

### Security
- Sekrety w `.env` (SECRET_KEY, DATABASE_URL). Plik `.env` w `.gitignore`.
- JWT z sensownym TTL (np. 30 minut access token).
- Hasła: bcrypt via passlib.
- Walidacja inputu: Pydantic schemas na każdym endpoincie.
- CORS: restrykcyjna allowlista (na MVP: tylko localhost + domena produkcyjna).
- Rate limiting: `slowapi` na endpointach auth.

### Struktura projektu
```
app/
  main.py          # FastAPI app, middleware, CORS
  config.py        # Settings z .env (pydantic-settings)
  database.py      # SQLAlchemy engine, session, Base
  models/          # SQLAlchemy models
  schemas/         # Pydantic schemas (request/response)
  routers/         # FastAPI routers (auth, notes, admin, uploads)
  services/        # Logika biznesowa
  dependencies.py  # Dependency injection (get_db, get_current_user)
tests/
  conftest.py      # Fixtures (test client, test db, test user)
  test_auth.py
  test_notes.py
  test_admin.py
  test_uploads.py
  test_export.py
  test_sharing.py
```

## Dobrze dodac pozniej

- **Pre-commit hooks:** ruff check + ruff format automatycznie przed commitem.
- **CI/CD:** GitHub Actions z pytest + ruff na każdym PR.
- **Logowanie:** `structlog` lub `loguru` dla strukturalnych logów.
- **Monitoring:** health endpoint + basic metrics.
- **Pagination:** offset/limit na listach notatek i userów.
- **Migracja na PostgreSQL:** zmiana DATABASE_URL + alembic migrate.

## Otwarte decyzje

- **Pagination stratgia:** offset/limit vs cursor-based — zdecydować gdy lista notatek urośnie.
- **File storage:** lokalny filesystem na MVP; jeśli potrzeba skalowania → S3-compatible (MinIO lub AWS S3).
- **Background tasks:** jeśli upload/eksport będzie wolny → FastAPI BackgroundTasks lub Celery.
