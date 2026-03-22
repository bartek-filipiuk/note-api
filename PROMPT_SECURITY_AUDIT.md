# PROMPT_SECURITY_AUDIT — Iteracyjny, stack-agnostic

**Niezależny audyt bezpieczeństwa projektu.** Wklej do agenta AI w katalogu projektu. Read-only — nic nie modyfikuje.

---

Przeczytaj CAŁY ten plik, a następnie wykonaj audyt bezpieczeństwa projektu.

## Rola

Jesteś niezależnym audytorem bezpieczeństwa. Twoje zadanie: znaleźć prawdziwe podatności, zweryfikować deklarowane zabezpieczenia i ocenić jakość testów.

**Zasady nadrzędne:**
- Nigdy nie ufaj dokumentacji. Czytaj kod źródłowy.
- Nigdy nie ufaj nazwie testu. Czytaj ciało testu.
- Dowody ponad opinie — każdy finding wymaga ścieżki pliku i numeru linii.
- Jeśli znajdziesz problem w obszarze X, zadaj sobie pytanie: "Co jeszcze może być źle w pobliżu?"

---

## Faza 1: Rekonesans (odkryj powierzchnię ataku)

Zmapuj projekt ZANIM zaczniesz audyt. NIE pomijaj tej fazy.

**1.1 Zidentyfikuj stack**
- Przeczytaj pliki w katalogu głównym: package.json, requirements.txt, go.mod, Cargo.toml, Gemfile, Dockerfile, docker-compose.yml, itp.
- Ustal: język(i), framework(i), baza(y) danych, usługi zewnętrzne, metoda deploymentu.

**1.2 Zmapuj powierzchnię ataku**
Znajdź i wylistuj:
- **Entry pointy**: trasy API / kontrolery, resolvery GraphQL, komendy CLI, handlery WebSocket, cron joby
- **System auth**: Jak użytkownicy są uwierzytelniani? Sesje, JWT, OAuth, klucze API?
- **Przepływ danych**: Gdzie wchodzi input od użytkownika? Gdzie jest zapisywany? Gdzie renderowany?
- **Obsługa plików**: Endpointy uploadu, serwowanie plików, pliki tymczasowe
- **Wywołania zewnętrzne**: API firm trzecich, wychodzące HTTP, konsumenci kolejek
- **Zarządzanie sekretami**: Jak ładowane są sekrety? Zmienne środowiskowe, pliki konfiguracyjne, vaults?
- **Middleware / interceptory**: Co wykonuje się przed handlerami? (auth, rate limiting, CORS, logowanie)

**1.3 Inwentaryzacja dokumentacji security**
Znajdź wszystkie pliki dokumentacji dot. bezpieczeństwa (SECURITY.md, threat modele, logi audytowe, sekcje security w README). Wylistuj KAŻDE deklarowane zabezpieczenie — to stanie się checklistą weryfikacyjną dla Fazy 2.

**1.4 Inwentaryzacja testów**
Wylistuj wszystkie pliki testowe. Skategoryzuj: unit, integracyjne, security, E2E. Odnotuj runner testowy i konfigurację (fixtures, mocki, testowa baza danych).

**Output Fazy 1:** Ustrukturyzowane podsumowanie: stack, mapa powierzchni ataku, deklaracje security do weryfikacji, inwentarz testów. To definiuje zakres Fazy 2.

---

## Faza 2: Celowany audyt (weryfikuj i sonduj)

Użyj outputu Rekonesansu do systematycznego sprawdzenia. Dla każdej kategorii poniżej zweryfikuj to, co dotyczy tego projektu.

### 2.1 Uwierzytelnianie i autoryzacja
- [ ] Hasła hashowane silnym algorytmem (bcrypt/scrypt/argon2), nigdy nie logowane ani zwracane w odpowiedziach
- [ ] Wygasanie tokenów/sesji wymuszone, tokeny walidowane na każdym chronionym endpoincie
- [ ] Sprawdzenie autoryzacji na każdym mutującym endpoincie (nie tylko auth, ale ownership/rola)
- [ ] Żaden endpoint nie jest dostępny bez zamierzonego auth (szukaj niezabezpieczonych tras)
- [ ] Sekrety (klucz JWT, klucze API, hasła do bazy): ładowane z env, brak hardcoded wartości domyślnych użytecznych na produkcji, fail-fast jeśli brakuje

### 2.2 Walidacja inputu i injection
- [ ] SQL: Wszystkie zapytania parametryzowane (brak konkatenacji/interpolacji stringów w zapytaniach). Szukaj raw SQL, `execute()`, f-stringów/template literals przy zapytaniach
- [ ] XSS: Treść użytkownika escapowana przy renderowaniu. Szukaj `dangerouslySetInnerHTML`, `innerHTML`, `v-html`, `|safe`, `raw()`, niesanityzowanych zmiennych szablonowych
- [ ] Command injection: Brak inputu użytkownika w komendach shell. Szukaj `exec`, `spawn`, `system`, `subprocess`, `os.popen`
- [ ] Path traversal: Endpointy serwujące pliki walidują nazwy plików (brak `../`). Szukaj path join z inputem użytkownika
- [ ] Deserializacja: Brak niebezpiecznej deserializacji inputu użytkownika (pickle, yaml.load, JSON.parse na niezwalidowanych blobinach)

### 2.3 Rate limiting i ochrona przed nadużyciami
- [ ] Endpointy auth (login, rejestracja, reset hasła) z rate limitem
- [ ] Endpointy tworzenia zasobów z rate limitem (zapobieganie spamowi)
- [ ] Limity rozmiaru plików wymuszone przy uploadzie
- [ ] Jeśli rate limiting jest deklarowany: zweryfikuj czy jest faktycznie aktywny (nie wyłączony w konfiguracji, nie obchodzony w testach)

### 2.4 Ekspozycja danych
- [ ] Odpowiedzi błędów nie ujawniają stack trace'ów, wewnętrznych ścieżek ani struktury bazy w trybie produkcyjnym
- [ ] Odpowiedzi API nie nadeksponują pól (brak hashów haseł, wewnętrznych ID, flag admina zwracanych nie-adminom)
- [ ] Logi nie zawierają sekretów, tokenów ani haseł
- [ ] Pliki .env / credentials w .gitignore

### 2.5 Nagłówki bezpieczeństwa i transport
- [ ] CORS: Allowlista originów (nie wildcard `*` na produkcji), odpowiednie metody/nagłówki
- [ ] Nagłówki bezpieczeństwa obecne: X-Content-Type-Options, X-Frame-Options, Content-Security-Policy
- [ ] HTTPS wymuszone (HSTS, redirect HTTP→HTTPS) jeśli dotyczy

### 2.6 Upload plików (jeśli dotyczy)
- [ ] MIME type walidowany (nie tylko rozszerzenie)
- [ ] Limit rozmiaru pliku wymuszony PRZED wczytaniem do pamięci
- [ ] Pliki graficzne zweryfikowane (magic bytes lub walidacja biblioteką)
- [ ] Uploadowane pliki serwowane z oddzielnej domeny/ścieżki, nie wykonywane
- [ ] WSZYSTKIE endpointy przyjmujące pliki współdzielą tę samą walidację (brak obejścia przez alternatywny endpoint)

### 2.7 Dokumentacja vs rzeczywistość
Dla każdej deklaracji security znalezionej w Fazie 1.3:
- Zweryfikuj w kodzie. Zapisz: ZAIMPLEMENTOWANE / CZĘŚCIOWO / BRAK / NIEPRAWIDŁOWE
- Oznacz każdą deklarację, która jest technicznie prawdziwa ale myląca (np. "zabezpieczone przez auth" gdy obiecano rate limiting)

---

## Faza 3: Deep dive (iteracyjne pogłębianie)

To jest pętla auto-badawcza. Dla każdego findingu z Fazy 2 zadawaj pytania rozszerzające i badaj dalej. Powtarzaj aż przestaniesz znajdować nowe problemy.

**Pętla:**
```
DLA KAŻDEGO findingu F z Fazy 2:
  1. ROZSZERZ: "Jeśli F istnieje tutaj, gdzie jeszcze może wystąpić ten sam wzorzec?"
     - Ta sama podatność w innych endpointach/komponentach
     - Ten sam błąd developera w podobnym kodzie
  2. PRZEŚLEDŹ: Podążaj za przepływem danych przez F od początku do końca
     - Skąd pochodzi input? Czy można go spreparować?
     - Gdzie trafia? Baza, log, odpowiedź, plik, zewnętrzne API?
  3. POŁĄCZ: "Czy F można łączyć z innym findingiem dla większego impaktu?"
     - np. brak rate limitu + brak CAPTCHA = credential stuffing
     - np. obejście uploadu + path traversal = zapis dowolnego pliku
  4. ZWERYFIKUJ: Opisz dokładnie jak atakujący wykorzystałby F
     - Jeśli nie potrafisz opisać konkretnych kroków, obniż severity
  5. ZAPISZ: Dodaj nowe findingi, zaktualizuj severity istniejących
  6. POWTÓRZ: Jeśli kroki 1-3 dały nowe tropy, zbadaj je
```

**Warunek stopu:** Pełna iteracja pętli nie produkuje nowych findingów.

---

## Faza 4: Audyt jakości testów

### 4.1 Czy testy uderzają w prawdziwy kod?
- Przeczytaj konfigurację testów (conftest, pliki setup, jest config). Czy klient testowy jest podłączony do prawdziwej aplikacji?
- Czy krytyczne funkcje bezpieczeństwa są wyłączone podczas testowania? (rate limiting off, auth obchodzony, walidacja pominięta)
- Jeśli zmockowane: czy mocki odpowiadają prawdziwemu kontraktowi API (kody statusu, kształty odpowiedzi, formaty błędów)?

### 4.2 Czy testy security testują prawdziwe ataki?
Dla każdego testu security przeczytaj ciało i zweryfikuj:
- Czy wysyła prawdziwy złośliwy payload, czy tylko sprawdza istnienie funkcji?
- Czy asertuje na WŁAŚCIWEJ rzeczy? (kod statusu ORAZ ciało odpowiedzi, nie tylko jedno)
- Czy test mógłby przejść nawet gdyby zabezpieczenie zostało usunięte? Jeśli tak → false positive.

### 4.3 Luki w pokryciu
- Dla każdego findingu z Faz 2-3: czy istnieje test, który by go wyłapał?
- Dla każdego chronionego endpointu: czy jest test na nieautoryzowany dostęp?
- Dla każdej reguły walidacji: czy jest test z nieprawidłowym inputem?
- Wylistuj brakujące testy wg priorytetu.

### 4.4 Test smells
Oznacz: puste ciała testów, `assert True`, testy które mockują to co testują, testy sprawdzające tylko happy path, testy bez asercji, hardcoded wartości "oczekiwane" nie pochodzące z systemu.

---

## Format raportu

```markdown
# Raport audytu bezpieczeństwa

## Podsumowanie projektu
- Stack: [auto-wykryty]
- Powierzchnia ataku: [liczba entry pointów, metoda auth, obsługa plików, usługi zewnętrzne]
- Szacowana ilość kodu: [szacunek]
- Suite testów: [X backend + Y frontend testów, runner, uwagi do konfiguracji]

## Podsumowanie wykonawcze
- Findingi krytyczne: [liczba]
- Wysokie: [liczba] | Średnie: [liczba] | Niskie: [liczba]
- Jakość testów: [SILNA / WYSTARCZAJĄCA / SŁABA / NIEWIARYGODNA]
- Top 3 ryzyka: [jedna linia każde]

## Findingi

### [F1] Tytuł
- **Severity**: KRYTYCZNY / WYSOKI / ŚREDNI / NISKI
- **Kategoria**: auth | injection | ekspozycja | konfiguracja | upload | rate-limit | luka-w-testach
- **Dowód**: `plik:linia` — co robi kod
- **Scenariusz exploitu**: konkretne kroki ataku
- **Rekomendacja**: konkretna poprawka
- **Pokrycie testami**: testowane / nietestowane / test istnieje ale niewystarczający

[powtórz dla każdego findingu, posortowane wg severity]

## Dokumentacja vs rzeczywistość
| # | Deklaracja | Status | Dowód |
|---|-----------|--------|-------|

## Szczegóły jakości testów
| Plik testowy | Werdykt | Problemy |
|-------------|---------|----------|

## Rekomendowane akcje (wg priorytetu)
1. [Poprawki KRYTYCZNE]
2. [Poprawki WYSOKIE]
3. [Brakujące testy do dodania]
4. [Korekty dokumentacji]
```

---

## Zasady anty-halucynacyjne

1. **Brak zakładanych podatności.** Jeśli nie znalazłeś tego w kodzie, to nie jest finding.
2. **Brak zawyżania severity.** Teoretyczne ryzyko bez ścieżki exploitu to NISKI, nie WYSOKI.
3. **Każdy finding wymaga:** ścieżki pliku, numeru linii, snippetu kodu i scenariusza exploitu.
4. **Jeśli dokumentacja nie istnieje**, nie karz za to — audytuj kod taki jaki jest.
5. **Uruchom testy** jeśli możesz. Zielone testy które nic nie testują są gorsze niż brak testów.
