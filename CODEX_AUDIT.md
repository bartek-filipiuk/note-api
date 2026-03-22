# Raport audytu bezpieczeństwa

Przejrzałem aktualny workspace repo, uruchomiłem testy i sprawdziłem zgodność z `PROMPT_SECURITY_AUDIT.md`. To jest FastAPI + SQLAlchemy + SQLite + JWT + bcrypt + slowapi, około 1.8k linii, 17 endpointów. `pytest -q` przechodzi: 46/46, ale jakość testów bezpieczeństwa oceniam jako `słabą`, bo nie łapią najpoważniejszych ścieżek.

## Najważniejsze problemy

1. **[Wysokie] IDOR na attachmentach prywatnych notatek**  
   Dowód: `app/routers/uploads.py:92`, `app/routers/uploads.py:103`.  
   `list_attachments()` i `download_attachment()` sprawdzają tylko istnienie notatki/załącznika, ale nie sprawdzają ownera, share ani `is_public`. Każdy zalogowany użytkownik może pobrać listę i plik z cudzej prywatnej notatki, jeśli zna `note_id`. Potwierdziłem to wykonawczo: obcy user dostał `200` na listę i pobranie pliku.

2. **[Średnie] Walidację uploadu da się obejść przez spoofing `Content-Type`**  
   Dowód: `app/routers/uploads.py:58`, `app/routers/uploads.py:79`.  
   Kod ufa `file.content_type` od klienta i nie sprawdza magic bytes. Potwierdziłem, że payload zaczynający się od `MZ` przesłany jako `image/png` jest akceptowany `201`. To przeczy deklaracji z `docs/SECURITY.md:12`.

3. **[Średnie] Limit 100 MB jest sprawdzany za późno, po pełnym wczytaniu pliku do RAM**  
   Dowód: `app/routers/uploads.py:64`.  
   `await file.read()` ładuje cały plik do pamięci, a dopiero potem jest `len(content) > MAX_FILE_SIZE`. To otwiera prosty wektor DoS na pamięć, zwłaszcza że endpoint nie ma rate limitu.

4. **[Średnie] Sekret JWT ma niebezpieczny domyślny fallback**  
   Dowód: `app/config.py:5`.  
   `SECRET_KEY = "change-me-in-production"` oznacza fail-open zamiast fail-fast. W środowisku uruchomionym bez poprawnego env atakujący może przewidzieć sekret i samodzielnie podpisywać tokeny. To jest sprzeczne z deklaracją z `docs/SECURITY.md:11`.

5. **[Średnie] Testy bezpieczeństwa nie pokrywają realnych wektorów ataku**  
   Dowód: `tests/test_uploads.py:59`, `tests/test_uploads.py:68`, `tests/test_auth.py:9`.  
   Brakuje testów na:
   - dostęp non-owner do `GET /notes/{id}/attachments`
   - dostęp non-owner do `GET /notes/{id}/attachments/{att_id}`
   - spoofing MIME przy dozwolonym `Content-Type`
   - oversize upload
   - rate limiting na `/auth/*`

## Co jest dobrze

- Hasła są hashowane bcryptem, a token JWT ma `exp` i jest walidowany na chronionych endpointach: `app/services/auth.py:8`, `app/dependencies.py:12`.
- Główna autoryzacja dla notatek, share, eksportu i admina wygląda sensownie: `app/routers/notes.py:49`, `app/routers/export.py:26`, `app/routers/admin.py:21`.
- Nie widzę raw SQL ani oczywistych injectionów; input wchodzi przez Pydantic, a `.env` i `uploads/` są w `.gitignore`: `app/schemas/auth.py:4`, `app/schemas/notes.py:6`, `.gitignore:1`.

## Dokumentacja vs rzeczywistość

- `IDOR ... każdy endpoint sprawdza owner_id lub share` z `docs/SECURITY.md:13`: `nieprawidłowe`.
- `Upload złośliwych plików ... MIME type validation, limit 100 MB` z `docs/SECURITY.md:12`: `częściowo / mylące`.
- `brak hardcoded secrets` z `docs/SECURITY.md:11`: `nieprawidłowe`.

## Rekomendowane akcje

1. Domknąć autoryzację na endpointach attachmentów, używając tych samych reguł dostępu co dla notatek.
2. Zrobić prawdziwą walidację uploadu: magic bytes i limit rozmiaru egzekwowany podczas streamowania, nie po `read()`.
3. Usunąć domyślny `SECRET_KEY` i wymusić fail-fast przy braku sekretu w env.
4. Dodać testy na brak autoryzacji attachmentów, spoofing MIME, oversize upload i rate limiting.
