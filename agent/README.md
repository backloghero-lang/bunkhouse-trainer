# Ziomek od Pokera — agent (Gemini + Cloudflare Worker)

Bezpieczny backend czatu. **Żaden klucz nie jest w repo** — siedzi jako *secret* w Cloudflare.
**Prompt edytujesz w pliku `agent/prompt.txt`** w repo: zmieniasz osobowość/zachowanie, commitujesz, a Worker sam zaciąga nową wersję (cache ~60 s).

## 1) Darmowy klucz Gemini (Google AI Studio)
1. Wejdź na **aistudio.google.com** → zaloguj kontem Google.
2. **Get API key** → **Create API key** → skopiuj klucz (`AIza...`).
3. NIE wklejaj go nigdzie poza Cloudflare (krok 3).

## 2) Wgraj nowy kod Workera
- Otwórz swojego Workera `pokerhouse-agent` → **Edit code** → zaznacz wszystko, skasuj, wklej całe `worker.js` z tego folderu → **Deploy**.

## 3) Zmienne i secret (Worker → Settings → Variables and Secrets)
- **Secret** `GEMINI_API_KEY` = Twój klucz `AIza...`
- (zostaw lub usuń stary `ANTHROPIC_API_KEY` — już nieużywany)
- **Text** `ALLOW_ORIGIN` = `https://backloghero-lang.github.io`
- (opcjonalne, Text — masz nad tym pełną kontrolę bez ruszania kodu):
  - `MODEL` = `gemini-2.5-flash`
  - `TEMPERATURE` = `0.85`  (wyżej = bardziej kreatywny/losowy)
  - `MAX_TOKENS` = `320`   (długość odpowiedzi)
  - `THINKING_BUDGET` = `512`  (budżet myślenia; `0` = bez myślenia/szybciej)
  - `PROMPT_URL` = własny adres pliku z promptem (domyślnie bierze `agent/prompt.txt` z repo)
- Kliknij Deploy/Save jeśli trzeba.

## 4) Edycja promptu (osobowość agenta)
- Otwórz `agent/prompt.txt`, zmień osobowość/zasady, **zachowaj `{{LANG}}`** (Worker podstawia tam język strony).
- Commit + push (np. `WYSLIJ-NA-GITHUB.bat`). Po max ~60 s Worker gada wg nowego promptu. Zero ruszania Cloudflare.

## Koszt / limit
- Gemini 2.5 Flash: darmowy tier (hojny). Limit pytań: front pokazuje licznik, a Worker z KV (`PB_KV`) egzekwuje twardo X/dzień na IP.

## Tryb właściciela (Ty bez limitu, reszta z limitem)
1. W Cloudflare (Worker → Settings → Variables) dodaj **Secret** `DEV_KEY` = dowolny wymyślony ciąg (np. `mojtajnyklucz123`). To NIE jest klucz API — to Twoje hasło-obejście.
2. Na swojej przeglądarce wejdź **raz** pod adres z parametrem:
   `https://backloghero-lang.github.io/bunkhouse-trainer/?pbdev=mojtajnyklucz123`
   (zamień na swój DEV_KEY). Front zapisze go w localStorage i od tej pory na tej przeglądarce masz **bez limitu** (licznik znika).
3. Goście bez tego klucza dalej mają limit (DAILY_LIMIT, domyślnie 5/dzień na IP — wymaga bindingu KV).
- Wyłączyć u siebie: w konsoli przeglądarki `localStorage.removeItem('pb_dev')`.

## Pamięć rozmowy
Agent pamięta wątek między podstronami w obrębie przeglądarki (historia w localStorage `pb_convo`, wysyłana do Workera jako kontekst). Wyczyścić: `localStorage.removeItem('pb_convo')`.
