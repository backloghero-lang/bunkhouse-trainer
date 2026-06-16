<p align="center">
  <img src="banner.png" alt="PokerHouse — trener turniejowego pokera" width="100%">
</p>

<h1 align="center">🂡 PokerHouse — trener turniejowego pokera</h1>

<p align="center">
  Ucz się push/fold, ICM i gry przy finałowym stole — <b>poza stołem</b>.<br>
  Prawdziwy silnik (Nash + ICM) liczy zakresy, a sarkastyczny <b>Bullet Bot</b> odpowiada na pytania o poker. Wszystko w przeglądarce.
</p>

<p align="center">
  <img alt="status" src="https://img.shields.io/badge/status-live-brightgreen">
  <img alt="hosting" src="https://img.shields.io/badge/hosting-GitHub%20Pages-blue">
  <img alt="silnik" src="https://img.shields.io/badge/silnik-Python%20%C2%B7%20Nash%20%2B%20ICM-3776AB">
  <img alt="czat" src="https://img.shields.io/badge/czat-Gemini%202.5%20Flash-FF9800">
  <img alt="vibe" src="https://img.shields.io/badge/vibe--coded%20z-Claude-8A63D2">
  <img alt="licencja" src="https://img.shields.io/badge/licencja-MIT-green">
</p>

<p align="center"><b>🔴 <a href="https://backloghero-lang.github.io/bunkhouse-trainer/">Zobacz na żywo →</a></b></p>

> ⚠️ Narzędzie do **nauki**, nie do podpowiedzi przy grze na żywo (off-table, bez RTA).

---

## ✨ Co potrafi

| | Sekcja | Co robi |
|---|---|---|
| 🎯 | **Trener ICM** | Ćwiczysz, kiedy iść all-in, a kiedy spasować na krótkim stacku. Wybierasz pozycję i stack (w blindach) — tabela 13×13 pokazuje gotowy zakres. Plus wykres bankrolla. |
| 🃏 | **Tabele push/fold** | 9-osobowy stół: klikasz miejsce, ustawiasz stack i masz zakres + procent rąk. |
| 🎬 | **Legendarne rozdania** | Filmy z najsłynniejszymi zagraniami w historii pokera. |
| 🏆 | **Galeria Sław** | Postacie, które tworzyły pokera (Brunson, Scotty Nguyen, Jack Strauss). |
| 📚 | **Nauka** | Linki do najlepszych szkół pokera (GTO Wizard, Upswing i inne). |
| 🔍 | **Analiza rozdań** | Wklejasz historię ręki z PokerStars / GGPoker — strona mówi, czy Twój all-in / fold był poprawny. |
| 🤖 | **Bullet Bot** | Sarkastyczny pokerowy asystent (czat). Odpowiada na pytania o poker i o stronę. Model Gemini, klucz schowany na serwerze. |

---

## 🧠 Jak to działa (bez bełkotu)

Zakresy push/fold wylicza silnik w Pythonie — model **Nasha i ICM** (czyli „ile naprawdę wart jest Twój stack w turnieju"). **Nic nie jest zgadywane.**
Strona to zwykłe pliki HTML hostowane za darmo na **GitHub Pages**, a czat dogaduje się z małym serwerem (**Cloudflare Worker**), żeby nie wystawiać klucza API w przeglądarce. Charakter bota edytujesz w jednym pliku tekstowym (`agent/prompt.txt`) — commit i gotowe.

```
[ przeglądarka ]  ──►  GitHub Pages (strona)
       │
       └─ czat ──►  Cloudflare Worker  ──►  Google Gemini
                    (ukryty klucz, limit per IP, prompt z repo)
```

---

## 🗂️ Co w środku

```
bunkhouse-trainer/
├── website/     # to, co widzisz w przeglądarce (wszystkie podstrony)
├── pushfold/    # silnik liczący (Python) + web/ranges.json (gotowe zakresy)
├── agent/       # mózg czatu Bullet Bota: worker.js + edytowalny prompt.txt
├── tests/       # 59 testów sprawdzających, że silnik liczy poprawnie
└── banner.png
```

---

## ⚖️ Uczciwie o ograniczeniach

- Zakresy **otwarcia** liczone na „chip-EV" — takie same niezależnie od fazy turnieju; ICM realnie zmienia zakres **obrony**, nie agresora.
- **Analiza rozdań** ocenia tylko krótkie stacki (≤ 20 BB) i tylko preflop — nie postflop.

## 🔒 Prywatność

Nic nie zbieramy — żadnego śledzenia, kont ani analityki. Ustawienia (język, licznik) siedzą tylko w Twojej przeglądarce. Klucze API są po stronie serwera, nigdy w kodzie strony.

---

## 🧑‍💻 O projekcie

**Projekt weekendowy, „zvibowany" z Claude** — zbudowany w parze z AI, dla zabawy i nauki. Strona powstała w ok. **3 dni robocze (3 MD)**.
Siostrzany projekt — wtyczka [PriceShift](https://github.com/backloghero-lang/priceshift) (porównywanie cen Allegro ↔ Amazon) — w ok. **2 dni (2 MD)**.

## 📝 Licencja

MIT — forkuj, zmieniaj, ucz się.

<p align="center">Nie do gry na żywo. Do nauki przy biurku. 🂡</p>
