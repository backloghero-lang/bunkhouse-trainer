# Bunkhouse — Final Table Trainer (push/fold Nash + ICM)

Narzędzie do nauki **off-table** push/fold w turniejowym NLHE. Deterministyczny silnik
(Nash + ICM) + interfejs webowy. **NIE do gry na żywo / RTA** — liczy wyłącznie ze
statycznego wejścia.

## Zawartość

- `pushfold/` — silnik (Python): equity (eval7), ICM Malmuth–Harville (DP O(2^n)),
  solvery push/fold HU/ICM/multiway/first-in pozycyjny, CLI/JSON, prekompilacja zakresów.
- `tests/` — 59 testów walidacyjnych (`pytest`).
- `web/` — samodzielny trener `bunkhouse_trainer.html` + `ranges.json` (zakresy prekompilowane).
- `app/` — nowoczesny front (React + Vite + shadcn) z wpiętymi prawdziwymi zakresami.
  Gotowy plik do otwarcia: `app/bunkhouse-app.html`. Źródło: `npm install && npm run dev`.

## Silnik — szybki start
```bash
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -q                      # walidacja
python -m pushfold.cli -f spot.json   # decyzja dla spotu (JSON in/out)
```

## Kamienie milowe (zwalidowane)
M0 setup · M1 equity · M2 HU cEV Nash · M3 ICM · M4 push/fold pod ICM ·
M5 multiway (3-handed + first-in) · M6 CLI/JSON · M7 ICM pozycyjny (+ DP O(2^n)).

## Ograniczenia (uczciwie)
Model multiway = „niezależni callerzy" (trzon zgodny, ręce graniczne do porównania z HRC/ICMIZER).
Otwarcia liczone w cEV (ICM prawie nie zmienia zakresu agresora); efekt ICM jest w obronie.
Werdykt w „Analizie rozdania" to placeholder do czasu parsera obrazu (Haiku).

Off-table study tool. Not for real-time use.
