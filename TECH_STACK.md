# Tech Stack — Notes API

## Backend

| Technologia | Uzasadnienie |
|------------|-------------|
| **Python 3.12+** | Stabilny, szeroko wspierany, świetny ekosystem dla API. |
| **FastAPI** | Szybki, async-ready, automatyczna dokumentacja Swagger/ReDoc, wbudowana walidacja via Pydantic. Idealny do REST API. |
| **SQLite** | Wystarczający dla ~100 userów. Zero konfiguracji. Łatwa migracja na PostgreSQL w przyszłości. |
| **SQLAlchemy 2.x** | ORM z parametryzowanymi zapytaniami (ochrona przed SQL Injection). Obsługuje SQLite i łatwo migruje na inne bazy. |
| **Alembic** | Migracje bazy danych — bezpieczne zmiany schematu w czasie rozwoju. |
| **Pydantic v2** | Walidacja inputu/outputu, schematy request/response. Zintegrowany z FastAPI. |
| **python-jose** | Generowanie i weryfikacja tokenów JWT. |
| **passlib[bcrypt]** | Bezpieczne hashowanie haseł (bcrypt). |
| **python-multipart** | Obsługa multipart/form-data (upload plików). |
| **uvicorn** | ASGI server do uruchamiania FastAPI. |

## Testowanie

| Technologia | Uzasadnienie |
|------------|-------------|
| **pytest** | Standard dla testów w Pythonie. |
| **httpx** | Async HTTP client, kompatybilny z TestClient FastAPI. |
| **pytest-cov** | Pokrycie kodu testami. |

## Infrastruktura

| Technologia | Uzasadnienie |
|------------|-------------|
| **Docker** | Konteneryzacja aplikacji, powtarzalne środowisko. |
| **Caddy** | Reverse proxy z automatycznym HTTPS (Let's Encrypt). Prostszy niż Nginx. |

## Rozważone alternatywy

| Kategoria | Alternatywa | Dlaczego odrzucona |
|----------|------------|-------------------|
| Framework | Django REST Framework | Zbyt ciężki dla prostego API. FastAPI jest lżejszy i szybszy. |
| Framework | Flask | Brak wbudowanej walidacji i auto-dokumentacji. Więcej boilerplate'u. |
| Baza danych | PostgreSQL | Overkill dla ~100 userów na MVP. SQLite wystarczy, migracja łatwa przez SQLAlchemy. |
| ORM | Tortoise ORM | Mniej dojrzały ekosystem niż SQLAlchemy. |
| Auth | authlib | python-jose jest prostszy dla samego JWT. |

## Frontend Styling

Pominięte — brak frontendu (patrz PRD: Look & Feel = N/A).
