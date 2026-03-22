# HANDOFF Stages Plan — Notes API

---

## Stage 1: Minimalna działająca aplikacja
**Cel:** Scaffolding projektu — FastAPI hello-world, SQLAlchemy + SQLite, pytest, Docker init, baseline security.
**User Stories:** (brak bezpośrednich US — infrastruktura pod wszystkie US)

### Taski:
- [x] T1: Scaffolding projektu — struktura katalogów (`app/`, `tests/`), `requirements.txt`, `app/main.py` z health endpoint `/health` (test → kod → verify)
- [x] T2: Konfiguracja SQLAlchemy + SQLite — `app/database.py`, `app/config.py` z pydantic-settings, `.env` z SECRET_KEY i DATABASE_URL (test → kod → verify)
- [x] T3: Integracja pytest — `tests/conftest.py` z TestClient i test DB (in-memory SQLite), test health endpointu (test → kod → verify)
- [x] T4: Dockerfile + docker-compose.yml (dev) — obraz Python, mount volume, uvicorn (test → kod → verify)
- [x] T5: CORS middleware — restrykcyjna allowlista (test → kod → verify)

### Security (MANDATORY w każdym stage):
- [x] S1: Sekrety w `.env`, plik `.env` w `.gitignore` — brak hardcoded secrets (Baseline #5)
- [x] S2: CORS restrykcyjny — allowlista origins (Baseline #6)
- [x] S3: Test security: request z niedozwolonego origin → brak CORS headers (Baseline #6)

### Docs (MANDATORY w każdym stage):
- [x] Update docs/CHANGELOG.md
- [x] Update docs/API.md (endpoint /health)
- [x] Update docs/README.md (Quick Start, struktura katalogów)

### Stage Completion (MANDATORY — wykonaj NA KOŃCU stage'u):
- [x] Self-check: zakres stage zgodny z PRD (infrastruktura gotowa)
- [x] Self-check: brak hardcoded secrets w kodzie
- [x] Self-check: testy zielone (funkcjonalne + security)
- [x] Zaktualizuj HANDOFF: WSZYSTKIE checkboxy tego stage → [x]

---

## Stage 2: Rejestracja, logowanie i autoryzacja
**Cel:** System auth — rejestracja, logowanie, JWT, endpoint whoami, hashowanie haseł.
**User Stories:** US-1, US-2, US-3

### Taski:
- [x] T1: Model User — SQLAlchemy model (id, email, hashed_password, is_admin, created_at) + Alembic init (test → kod → verify)
- [x] T2: Endpoint POST /auth/register — rejestracja z walidacją email/hasło, zwrotka z tokenem JWT (test → kod → verify)
- [x] T3: Endpoint POST /auth/login — logowanie, zwrotka z tokenem JWT (test → kod → verify)
- [x] T4: Dependency `get_current_user` — dekodowanie JWT, pobieranie usera z DB (test → kod → verify)
- [x] T5: Endpoint GET /auth/whoami — dane zalogowanego usera (test → kod → verify)

### Security (MANDATORY w każdym stage):
- [x] S1: Hasła hashowane bcrypt via passlib — nigdy plaintext (Baseline #7)
- [x] S2: JWT z TTL (30 min) — token expiry weryfikowany (Baseline #7)
- [x] S3: Walidacja inputu rejestracji — Pydantic schema: email format, hasło min. 8 znaków (Baseline #2)
- [x] S4: Rate limiting na POST /auth/register i POST /auth/login — slowapi, max 5 req/min per IP (Baseline #8, PRD: brute force)
- [x] S5: Test security: rejestracja z duplikatem email → 409 (Baseline #2)
- [x] S6: Test security: login z błędnym hasłem → 401 (Baseline #7)
- [x] S7: Test security: request bez tokena na /auth/whoami → 401 (Baseline #1)
- [x] S8: Test security: request z wygasłym tokenem → 401 (Baseline #7)

### Docs (MANDATORY w każdym stage):
- [x] Update docs/CHANGELOG.md
- [x] Update docs/API.md (endpoints /auth/register, /auth/login, /auth/whoami)
- [x] Update docs/README.md (jeśli zmieniła się struktura, Quick Start lub zależności)

### Stage Completion (MANDATORY — wykonaj NA KOŃCU stage'u):
- [x] Self-check: zakres stage zgodny z PRD (US-1, US-2, US-3 pokryte)
- [x] Self-check: brak hardcoded secrets w kodzie
- [x] Self-check: testy zielone (funkcjonalne + security)
- [x] Zaktualizuj HANDOFF: WSZYSTKIE checkboxy tego stage → [x]

---

## Stage 3: CRUD na notatkach
**Cel:** Pełny CRUD notatek — tworzenie, listowanie, szczegóły, edycja, usuwanie. Tagi i flaga public/private.
**User Stories:** US-4, US-5, US-6, US-7

### Taski:
- [x] T1: Model Note — SQLAlchemy model (id, title, content, tags JSON, is_public, owner_id FK, created_at, updated_at) (test → kod → verify)
- [x] T2: Endpoint POST /notes — tworzenie notatki przez zalogowanego usera (test → kod → verify)
- [x] T3: Endpoint GET /notes — lista notatek zalogowanego usera (test → kod → verify)
- [x] T4: Endpoint GET /notes/{id} — szczegóły notatki (tylko własna, udostępniona lub publiczna) (test → kod → verify)
- [x] T5: Endpoint PUT /notes/{id} — edycja notatki (tylko właściciel) (test → kod → verify)
- [x] T6: Endpoint DELETE /notes/{id} — usuwanie notatki (tylko właściciel) (test → kod → verify)

### Security (MANDATORY w każdym stage):
- [x] S1: Walidacja inputu — Pydantic schema: title wymagany, content wymagany, tags lista stringów (Baseline #2)
- [x] S2: Autoryzacja: każdy endpoint sprawdza owner_id — IDOR protection (PRD: IDOR)
- [x] S3: ORM z parametryzowanymi zapytaniami — brak raw SQL (Baseline #3)
- [x] S4: Test security: edycja cudzej notatki → 403 (PRD: IDOR)
- [x] S5: Test security: usunięcie cudzej notatki → 403 (PRD: IDOR)
- [x] S6: Test security: dostęp do prywatnej cudzej notatki → 403 (PRD: nieautoryzowany dostęp)

### Docs (MANDATORY w każdym stage):
- [x] Update docs/CHANGELOG.md
- [x] Update docs/API.md (endpoints /notes CRUD)
- [x] Update docs/README.md (jeśli zmieniła się struktura, Quick Start lub zależności)

### Stage Completion (MANDATORY — wykonaj NA KOŃCU stage'u):
- [x] Self-check: zakres stage zgodny z PRD (US-4, US-5, US-6, US-7 pokryte)
- [x] Self-check: brak hardcoded secrets w kodzie
- [x] Self-check: testy zielone (funkcjonalne + security)
- [x] Zaktualizuj HANDOFF: WSZYSTKIE checkboxy tego stage → [x]

---

## Stage 4: Wyszukiwanie po tagach i udostępnianie notatek
**Cel:** Wyszukiwanie notatek po tagu oraz udostępnianie notatki wielu userom (read-only).
**User Stories:** US-8, US-9

### Taski:
- [x] T1: Endpoint GET /notes?tag=nazwa — filtrowanie notatek po tagu (własne + udostępnione + publiczne) (test → kod → verify)
- [x] T2: Model NoteShare — SQLAlchemy model (id, note_id FK, shared_with_user_id FK, created_at) (test → kod → verify)
- [x] T3: Endpoint POST /notes/{id}/share — udostępnienie notatki userowi po ID (tylko właściciel) (test → kod → verify)
- [x] T4: Endpoint DELETE /notes/{id}/share/{user_id} — cofnięcie udostępnienia (tylko właściciel) (test → kod → verify)
- [x] T5: Aktualizacja GET /notes i GET /notes/{id} — uwzględnienie notatek udostępnionych (test → kod → verify)

### Security (MANDATORY w każdym stage):
- [x] S1: Tylko właściciel może udostępniać/cofać udostępnienie — autoryzacja (PRD: IDOR)
- [x] S2: Walidacja: udostępnienie nieistniejącemu userowi → 404 (Baseline #2)
- [x] S3: Odbiorca nie może edytować/usuwać udostępnionej notatki → 403 (PRD: nieautoryzowany dostęp)
- [x] S4: Test security: share cudzej notatki → 403 (PRD: IDOR)
- [x] S5: Test security: edycja udostępnionej notatki przez odbiorcę → 403

### Docs (MANDATORY w każdym stage):
- [x] Update docs/CHANGELOG.md
- [x] Update docs/API.md (endpoints /notes?tag=, /notes/{id}/share)
- [x] Update docs/README.md (jeśli zmieniła się struktura, Quick Start lub zależności)

### Stage Completion (MANDATORY — wykonaj NA KOŃCU stage'u):
- [x] Self-check: zakres stage zgodny z PRD (US-8, US-9 pokryte)
- [x] Self-check: brak hardcoded secrets w kodzie
- [x] Self-check: testy zielone (funkcjonalne + security)
- [x] Zaktualizuj HANDOFF: WSZYSTKIE checkboxy tego stage → [x]

---

## Stage 5: Upload obrazków
**Cel:** Upload obrazków jako załączników do notatek. Przechowywanie na filesystem.
**User Stories:** US-10

### Taski:
- [ ] T1: Model Attachment — SQLAlchemy model (id, note_id FK, filename, original_filename, mime_type, size_bytes, created_at) (test → kod → verify)
- [ ] T2: Endpoint POST /notes/{id}/attachments — upload obrazka (multipart/form-data) (test → kod → verify)
- [ ] T3: Endpoint GET /notes/{id}/attachments — lista załączników notatki (test → kod → verify)
- [ ] T4: Endpoint GET /notes/{id}/attachments/{attachment_id} — pobranie pliku (test → kod → verify)
- [ ] T5: Endpoint DELETE /notes/{id}/attachments/{attachment_id} — usunięcie załącznika (tylko właściciel) (test → kod → verify)
- [ ] T6: Katalog uploads/ poza kodem źródłowym, dodany do .gitignore (test → kod → verify)

### Security (MANDATORY w każdym stage):
- [ ] S1: Walidacja MIME type — tylko JPEG, PNG, GIF, WebP (PRD: upload złośliwych plików)
- [ ] S2: Limit rozmiaru pliku — max 100 MB (PRD: upload złośliwych plików)
- [ ] S3: Filename sanitization — unikalny UUID, oryginalna nazwa w DB (PRD: upload złośliwych plików)
- [ ] S4: Tylko właściciel notatki może uploadować/usuwać załączniki (PRD: IDOR)
- [ ] S5: Test security: upload pliku .exe → 400 (PRD: upload złośliwych plików)
- [ ] S6: Test security: upload pliku > 100 MB → 413 (PRD: upload złośliwych plików)
- [ ] S7: Test security: upload do cudzej notatki → 403 (PRD: IDOR)

### Docs (MANDATORY w każdym stage):
- [ ] Update docs/CHANGELOG.md
- [ ] Update docs/API.md (endpoints /notes/{id}/attachments)
- [ ] Update docs/README.md (informacja o katalogu uploads/)

### Stage Completion (MANDATORY — wykonaj NA KOŃCU stage'u):
- [ ] Self-check: zakres stage zgodny z PRD (US-10 pokryte)
- [ ] Self-check: brak hardcoded secrets w kodzie
- [ ] Self-check: testy zielone (funkcjonalne + security)
- [ ] Zaktualizuj HANDOFF: WSZYSTKIE checkboxy tego stage → [x]

---

## Stage 6: Eksport notatek i panel admina
**Cel:** Eksport notatki do .txt oraz endpoint admina do listowania userów.
**User Stories:** US-11, US-12

### Taski:
- [ ] T1: Endpoint GET /notes/{id}/export — generowanie pliku .txt (tytuł, treść, tagi), Content-Disposition attachment (test → kod → verify)
- [ ] T2: Endpoint GET /admin/users — lista userów (id, email, created_at), dostęp tylko is_admin (test → kod → verify)
- [ ] T3: Dependency `require_admin` — sprawdzenie is_admin, reużywalna zależność (test → kod → verify)

### Security (MANDATORY w każdym stage):
- [ ] S1: Eksport tylko własnej notatki lub udostępnionej — autoryzacja (PRD: IDOR)
- [ ] S2: Endpoint admina zabezpieczony flagą is_admin — zwykły user → 403 (PRD: ekspozycja danych admina)
- [ ] S3: Test security: eksport cudzej prywatnej notatki → 403 (PRD: IDOR)
- [ ] S4: Test security: GET /admin/users jako zwykły user → 403 (PRD: ekspozycja danych admina)
- [ ] S5: Test security: GET /admin/users bez tokena → 401 (Baseline #1)

### Docs (MANDATORY w każdym stage):
- [ ] Update docs/CHANGELOG.md
- [ ] Update docs/API.md (endpoints /notes/{id}/export, /admin/users)
- [ ] Update docs/README.md (jeśli zmieniła się struktura, Quick Start lub zależności)

### Stage Completion (MANDATORY — wykonaj NA KOŃCU stage'u):
- [ ] Self-check: zakres stage zgodny z PRD (US-11, US-12 pokryte)
- [ ] Self-check: brak hardcoded secrets w kodzie
- [ ] Self-check: testy zielone (funkcjonalne + security)
- [ ] Zaktualizuj HANDOFF: WSZYSTKIE checkboxy tego stage → [x]

---

## Stage 7: Dopracowanie i finalizacja
**Cel:** Szlify — review kodu, poprawa edge case'ów, finalizacja dokumentacji, przygotowanie do deploymentu.
**User Stories:** (wszystkie — weryfikacja kompletności)

### Taski:
- [ ] T1: Code review — przegląd wszystkich modułów pod kątem edge case'ów, spójności, czytelności (test → kod → verify)
- [ ] T2: Finalizacja docs/README.md — kompletny Quick Start, pełna struktura katalogów (test → kod → verify)
- [ ] T3: Finalizacja docs/API.md — kompletna dokumentacja wszystkich endpointów (test → kod → verify)
- [ ] T4: Przygotowanie produkcyjnego docker-compose.yml i Dockerfile (test → kod → verify)
- [ ] T5: Przygotowanie Caddyfile z reverse proxy i HTTPS (test → kod → verify)

### Security (MANDATORY w każdym stage):
- [ ] S1: Przegląd nagłówków bezpieczeństwa — Content-Security-Policy, X-Content-Type-Options, X-Frame-Options (Baseline #6)
- [ ] S2: Weryfikacja że wszystkie endpointy wymagają auth (oprócz /health, /auth/register, /auth/login) (Baseline #1)
- [ ] S3: Finalne sprawdzenie: brak hardcoded secrets w całym kodzie (Baseline #5)
- [ ] S4: Test security: smoke test — niepoprawny input, nieautoryzowane żądania, expired token

### Docs (MANDATORY w każdym stage):
- [ ] Update docs/CHANGELOG.md (wpis finalizacyjny)
- [ ] Update docs/API.md (finalna weryfikacja kompletności)
- [ ] Update docs/README.md (finalna weryfikacja)

### Stage Completion (MANDATORY — wykonaj NA KOŃCU stage'u):
- [ ] Self-check: zakres stage zgodny z PRD (wszystkie US pokryte we wcześniejszych stage'ach)
- [ ] Self-check: brak hardcoded secrets w kodzie
- [ ] Self-check: testy zielone (funkcjonalne + security)
- [ ] Zaktualizuj HANDOFF: WSZYSTKIE checkboxy tego stage → [x]

---

## Coverage Check vs PRD

| User Story | Stage(s) |
|-----------|----------|
| US-1: Rejestracja | Stage 2 |
| US-2: Logowanie | Stage 2 |
| US-3: Whoami | Stage 2 |
| US-4: Tworzenie notatek | Stage 3 |
| US-5: Przeglądanie notatek | Stage 3 + Stage 4 (udostępnione) |
| US-6: Edycja notatek | Stage 3 |
| US-7: Usuwanie notatek | Stage 3 |
| US-8: Wyszukiwanie po tagu | Stage 4 |
| US-9: Udostępnianie notatek | Stage 4 |
| US-10: Upload obrazków | Stage 5 |
| US-11: Eksport do .txt | Stage 6 |
| US-12: Admin — lista userów | Stage 6 |

---

## Security Traceability

| Wymaganie security | Źródło | Stage | Task |
|-------------------|--------|-------|------|
| API auth + autoryzacja | Baseline #1 | Stage 2 | T4: Dependency get_current_user |
| Walidacja i sanityzacja inputu | Baseline #2 | Stage 2 | S3: Walidacja Pydantic rejestracji |
| Walidacja i sanityzacja inputu | Baseline #2 | Stage 3 | S1: Walidacja Pydantic notatek |
| Ochrona przed SQL Injection (ORM) | Baseline #3 | Stage 3 | S3: ORM z parametryzowanymi zapytaniami |
| Ochrona przed XSS | Baseline #4 | Stage 3 | S1: Pydantic sanityzacja (API zwraca JSON) |
| Sekrety poza kodem (.env) | Baseline #5 | Stage 1 | S1: .env + .gitignore |
| CORS restrykcyjny + nagłówki | Baseline #6 | Stage 1 | S2: CORS allowlista |
| CORS restrykcyjny + nagłówki | Baseline #6 | Stage 7 | S1: Nagłówki bezpieczeństwa |
| Hashowanie haseł + TTL sesji | Baseline #7 | Stage 2 | S1: bcrypt + S2: JWT TTL |
| Rate limiting / brute force | Baseline #8 | Stage 2 | S4: slowapi na auth endpoints |
| Testy security (negative cases) | Baseline #9 | Stage 1-7 | Sekcja Security w każdym stage |
| API abuse / brute force login | PRD: threat model | Stage 2 | S4: Rate limiting na auth |
| SQL Injection | PRD: threat model | Stage 3 | S3: ORM parametryzowane zapytania |
| XSS via treść notatki | PRD: threat model | Stage 3 | S1: Pydantic + JSON response |
| Nieautoryzowany dostęp do notatek | PRD: threat model | Stage 3 | S2: Autoryzacja owner_id, IDOR |
| Wyciek sekretów | PRD: threat model | Stage 1 | S1: .env w .gitignore |
| Upload złośliwych plików | PRD: threat model | Stage 5 | S1-S3: MIME, rozmiar, sanitization |
| IDOR | PRD: threat model | Stage 3-6 | S2/S4/S5: sprawdzenie owner_id |
| Ekspozycja danych admina | PRD: threat model | Stage 6 | S2: is_admin check |
