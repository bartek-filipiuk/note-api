Prosty REST API (FastAPI), gdzie użytkownicy mogą się rejestrować, logować, tworzyć prywatne notatki tekstowe, 
tagować je i opcjonalnie udostępniać innym użytkownikom po ich ID. 
API obsługuje CRUD na notatkach, wyszukiwanie po tagach, eksport notatek do pliku oraz endpoint 
administracyjny do listowania wszystkich użytkowników. Dane trzymane w bazie sql, autentykacja przez token, 
upload załączników (obrazki) do notatek.

Notes API — MVP
Rejestracja i logowanie (email + hasło), zwrotka z tokenem. Endpoint "whoami" zwracający dane usera. 
CRUD na notatkach — tytuł, treść, tagi (lista stringów), flaga public/private. 
Wyszukiwanie notatek po tagu (query param). Udostępnianie notatki konkretnemu userowi po ID. 
Upload obrazka jako załącznik do notatki. 
Eksport pojedynczej notatki do pliku .txt (generowany na serwerze, zwracany do pobrania). 
Jeden endpoint admina: lista wszystkich userów.
