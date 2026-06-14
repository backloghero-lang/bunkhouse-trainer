# Ziomek od Pokera — agent (backend)

Bezpieczny backend dla czatu na stronie. **Klucz API NIGDY nie trafia do repo ani do przeglądarki** — siedzi jako *secret* w Cloudflare.

## Wdrożenie przez panel Cloudflare (bez instalowania niczego)

1. Załóż darmowe konto na **cloudflare.com** → wejdź w **Workers & Pages** → **Create application** → **Create Worker** → nadaj nazwę (np. `pokerhouse-agent`) → **Deploy**.
2. **Edit code** → wklej całą zawartość `worker.js` z tego folderu → **Deploy**.
3. **Settings → Variables and Secrets**:
   - Dodaj **Secret** o nazwie `ANTHROPIC_API_KEY` i wartości = Twój klucz z konsoli Anthropic (zaszyfrowany, nie pokaże się w repo).
   - Dodaj zwykłą zmienną `ALLOW_ORIGIN` = adres Twojej strony, np. `https://backloghero-lang.github.io` (chroni przed wołaniem z obcych stron).
   - (opcjonalnie) `DAILY_LIMIT` = `5`.
4. (opcjonalnie, ale zalecane — twardy limit po IP) **Workers & Pages → KV → Create namespace** (np. `pb_limits`). Potem w Workerze **Settings → Bindings → Add → KV namespace**, nazwa zmiennej **`PB_KV`**, wskaż utworzony namespace.
5. Skopiuj adres Workera (coś jak `https://pokerhouse-agent.twojanazwa.workers.dev`).
6. W stronie wklej ten adres do stałej `PB_API` (jest na górze skryptu bota na każdej stronie) i wypchnij stronę na GitHub.

Gotowe — czat woła Twój Worker, Worker woła Anthropic swoim ukrytym kluczem.

## Limity i koszt
- Model: `claude-haiku-4-5` (najtańszy), `max_tokens: 300` → jedno pytanie to ułamek centa.
- Limit pytań: front pokazuje licznik (5), a Worker z KV egzekwuje twardo 5/dzień na IP. Bez KV limit pilnuje tylko front (łatwiej obejść — wtedy ustaw niski `DAILY_LIMIT` i obserwuj zużycie w panelu Anthropic).
- System prompt wymusza: tylko poker + ta strona, charakter „ziomka", odpowiedź w języku strony.

## Alternatywa: Vercel/Netlify
Ten sam `worker.js` da się przepisać na funkcję `/api/chat` (Node) — daj znać, dorzucę wersję.
