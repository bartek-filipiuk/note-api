# PRD — Notes API

## Wizja projektu / cele

Prosty, bezpieczny REST API do zarządzania prywatnymi notatkami tekstowymi. Użytkownicy mogą się rejestrować, logować, tworzyć notatki z tagami, udostępniać je innym użytkownikom (read-only) oraz załączać obrazki. API obsługuje eksport notatek do pliku `.txt` i posiada podstawowy panel administracyjny (endpoint do listowania userów).

**Cel MVP:** Działające API z pełnym CRUD na notatkach, systemem auth, udostępnianiem, uploadem obrazków i eksportem — gotowe do wdrożenia na VPS.

**Docelowi użytkownicy:** Początkowo do ~100 osób, z możliwością wzrostu.

---

## User Stories

### Rejestracja i logowanie
- **US-1:** Jako nowy użytkownik chcę się zarejestrować podając email i hasło, aby uzyskać konto.
  - *Kryteria akceptacji:* Endpoint POST zwraca token po poprawnej rejestracji. Email musi być unikalny. Hasło jest walidowane (min. 8 znaków). Błędy zwracają sensowne komunikaty.
- **US-2:** Jako użytkownik chcę się zalogować emailem i hasłem, aby otrzymać token dostępu.
  - *Kryteria akceptacji:* Endpoint POST zwraca token JWT. Błędne dane → 401. Token ma sensowne TTL.
- **US-3:** Jako zalogowany użytkownik chcę wywołać endpoint "whoami", aby sprawdzić swoje dane.
  - *Kryteria akceptacji:* GET zwraca id, email i rolę aktualnie zalogowanego usera. Bez tokena → 401.

### CRUD na notatkach
- **US-4:** Jako zalogowany użytkownik chcę tworzyć notatki (tytuł, treść, tagi, flaga public/private).
  - *Kryteria akceptacji:* POST tworzy notatkę przypisaną do zalogowanego usera. Tagi to lista stringów. Domyślnie notatka jest private.
- **US-5:** Jako zalogowany użytkownik chcę przeglądać swoje notatki (lista + szczegóły).
  - *Kryteria akceptacji:* GET lista zwraca notatki zalogowanego usera. GET po ID zwraca szczegóły notatki (tylko własnej lub udostępnionej/publicznej).
- **US-6:** Jako zalogowany użytkownik chcę edytować swoje notatki.
  - *Kryteria akceptacji:* PUT/PATCH aktualizuje notatkę. Tylko właściciel może edytować. Inny user → 403.
- **US-7:** Jako zalogowany użytkownik chcę usuwać swoje notatki.
  - *Kryteria akceptacji:* DELETE usuwa notatkę. Tylko właściciel może usunąć. Inny user → 403.

### Wyszukiwanie i udostępnianie
- **US-8:** Jako zalogowany użytkownik chcę wyszukiwać notatki po tagu.
  - *Kryteria akceptacji:* GET z query param `?tag=nazwa` zwraca notatki (własne + udostępnione + publiczne) pasujące do tagu.
- **US-9:** Jako właściciel notatki chcę udostępnić ją konkretnemu userowi (lub wielu) po ich ID — tylko do odczytu.
  - *Kryteria akceptacji:* POST endpoint dodaje uprawnienie odczytu. Można udostępnić wielu userom. Odbiorca widzi notatkę w swoim widoku, ale nie może edytować/usuwać.

### Upload załączników
- **US-10:** Jako zalogowany użytkownik chcę dodać obrazek jako załącznik do notatki.
  - *Kryteria akceptacji:* POST multipart upload. Max rozmiar pliku: 100 MB. Akceptowane formaty: JPEG, PNG, GIF, WebP. Obrazek powiązany z notatką. Tylko właściciel notatki może uploadować.

### Eksport
- **US-11:** Jako zalogowany użytkownik chcę wyeksportować pojedynczą notatkę do pliku `.txt`.
  - *Kryteria akceptacji:* GET endpoint generuje plik `.txt` z tytułem, treścią i tagami. Zwraca plik do pobrania (Content-Disposition). Tylko właściciel lub user z dostępem.

### Admin
- **US-12:** Jako admin chcę zobaczyć listę wszystkich zarejestrowanych użytkowników.
  - *Kryteria akceptacji:* GET endpoint zwraca listę userów (id, email, data rejestracji). Dostęp tylko dla usera z `is_admin=True`. Zwykły user → 403.

---

## Scope

### IN (MVP)
- Rejestracja i logowanie (email + hasło, JWT)
- Endpoint whoami
- CRUD na notatkach (tytuł, treść, tagi, public/private)
- Wyszukiwanie notatek po tagu
- Udostępnianie notatki wielu userom (read-only) po ich ID
- Upload obrazków do notatek (max 100 MB, filesystem)
- Eksport notatki do .txt
- Endpoint admina: lista userów (flaga is_admin)
- Baza danych: SQLite
- Autentykacja: JWT token
- Dokumentacja API (automatyczna via FastAPI/Swagger)

### OUT (poza MVP)
- Frontend / UI
- Rejestracja przez OAuth / social login
- Edycja notatek przez osoby, którym udostępniono
- Komentarze do notatek
- Wersjonowanie notatek
- Wyszukiwanie pełnotekstowe
- Powiadomienia (email, push)
- Eksport do PDF/Markdown
- Upload wielu plików naraz
- Panel admina z UI
- Usuwanie/banowanie userów przez admina
- Storage w chmurze (S3)
- CI/CD pipeline

---

## Zagrożenia / mini-threat model

| Zagrożenie | Prawdopodobieństwo | Wpływ | Mitygacja |
|-----------|-------------------|-------|-----------|
| **API abuse / brute force login** | Wysokie | Średni | Rate limiting na endpointach auth (rejestracja, login). Sensowne TTL tokenów. |
| **SQL Injection** | Średnie | Krytyczny | ORM (SQLAlchemy) z zapytaniami parametryzowanymi. Brak surowego SQL z inputem użytkownika. |
| **XSS via treść notatki** | Średnie | Średni | API zwraca JSON — brak renderowania HTML. Sanityzacja inputu. |
| **Nieautoryzowany dostęp do notatek** | Wysokie | Krytyczny | Autoryzacja na poziomie każdego endpointu: sprawdzenie owner_id lub uprawnień share. |
| **Wyciek sekretów** | Średnie | Krytyczny | Sekrety w `.env`, plik w `.gitignore`. Brak hardcoded tokenów/kluczy. |
| **Upload złośliwych plików** | Średnie | Wysoki | Walidacja MIME type + rozszerzenia. Limit rozmiaru (100 MB). Przechowywanie poza katalogiem kodu. |
| **IDOR (Insecure Direct Object Reference)** | Wysokie | Krytyczny | Każdy endpoint sprawdza, czy zalogowany user ma prawo do zasobu. |
| **Ekspozycja danych admina** | Niskie | Wysoki | Endpoint admina zabezpieczony sprawdzeniem flagi `is_admin`. |

---

## Wymagania niefunkcjonalne

- **Wydajność:** API powinno obsłużyć ~100 równoczesnych użytkowników bez degradacji.
- **Utrzymywalność / agent-friendly codebase:**
  - Modularny kod: oddzielne moduły dla auth, notes, admin, uploads.
  - Jawne kontrakty API (Pydantic schemas dla request/response).
  - Przewidywalna struktura katalogów.
  - Brak ukrytych zależności — dependency injection via FastAPI.
- **Testowalność:** Pełne pokrycie testami (pytest), TDD.
- **Bezpieczeństwo:** Patrz sekcja "Zagrożenia" + Minimum Security Baseline z AGENT_INIT_PROMPT.

---

## Look & Feel

**N/A — brak frontendu.** Aplikacja to czyste REST API. Interfejs użytkownika to dokumentacja Swagger/ReDoc generowana automatycznie przez FastAPI.
