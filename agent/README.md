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
