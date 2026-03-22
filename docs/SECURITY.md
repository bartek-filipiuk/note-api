# Security — Notes API

## Threat model (na bazie PRD)

| Zagrożenie | Mitygacja | Status |
|-----------|-----------|--------|
| API abuse / brute force login | Rate limiting 5/min na /auth/register i /auth/login (slowapi) | Wdrożone |
| SQL Injection | SQLAlchemy ORM z parametryzowanymi zapytaniami, brak raw SQL | Wdrożone |
| XSS via treść notatki | API zwraca JSON, brak renderowania HTML. Pydantic sanityzacja | Wdrożone |
| Nieautoryzowany dostęp do notatek | Autoryzacja owner_id na każdym endpoincie, IDOR protection | Wdrożone |
| Wyciek sekretów | .env w .gitignore, brak hardcoded secrets | Wdrożone |
| Upload złośliwych plików | MIME type validation (JPEG/PNG/GIF/WebP), limit 100 MB, UUID filenames | Wdrożone |
| IDOR | Każdy endpoint sprawdza owner_id lub uprawnienia share | Wdrożone |
| Ekspozycja danych admina | Endpoint /admin/users zabezpieczony flagą is_admin | Wdrożone |

## Wdrożone zabezpieczenia

- **Auth:** JWT z TTL 30 min, bcrypt hashowanie haseł
- **Rate limiting:** slowapi na endpointach auth (5/min per IP)
- **Input validation:** Pydantic schemas na wszystkich endpointach, email format, password min. 8 chars
- **CORS:** Restrykcyjna allowlista origins
- **Security headers:** X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, Content-Security-Policy
- **File upload:** MIME type whitelist, 100 MB limit, UUID filenames (sanitization)
- **Autoryzacja:** owner_id check na CRUD, share access check, admin flag check
- **Sekrety:** .env file, .gitignore protection

## Znane ograniczenia

- SQLite nie wspiera row-level locking — dla >100 concurrent users rozważyć PostgreSQL
- Rate limiting per IP — za NAT wielu userów może mieć ten sam IP
- Brak refresh tokenów — access token 30 min, potem ponowne logowanie
- Brak szyfrowania plików at-rest w katalogu uploads/
- Brak audit logu operacji (kto, co, kiedy)
- Brak 2FA / MFA
