# HANDOFF — Trainer push/fold (Nash + ICM) dla turniejowego NLHE

> Dokument startowy projektu. Wrzuć go jako pierwszy kontekst w nowej sesji Claude Code lub Cowork.
> Agent ma traktować ten plik jako źródło prawdy o zakresie, ograniczeniach i kolejności prac.

---

## 0. TWARDE OGRANICZENIA (przeczytaj najpierw)

- **To narzędzie do nauki off-table (review po sesji), NIE do użycia w trakcie gry.**
- Pod żadnym pozorem nie budujemy integracji ze stołem na żywo, nasłuchu okna klienta pokerowego, auto-czytania kart z aktywnej gry ani niczego, co działa w czasie rzeczywistym podczas grania.
- Powód: użycie solvera w trakcie gry = RTA (Real-Time Assistance) = łamanie regulaminu GGPoker (i każdego dużego roomu) = permanentny ban + konfiskata środków. Solverów do **nauki** używać wolno; w trakcie gry — nie.
- Każda funkcja, którą dodajemy, musi mieć sens w kontekście „analizuję rozdanie po fakcie / drilluję spoty". Jeśli jakiś pomysł ma sens tylko przy stole na żywo — odrzucamy go.
- **Funkcja „Analiza rozdania" (wrzucanie zdjęć) = review PO rozdaniu, nie podpowiadacz na żywo.** Wrzucasz screen ze swojej historii / zakończonej ręki, narzędzie pokazuje co było GTO (push/fold lub raise), a Ty porównujesz to ze swoją decyzją. To jest DOZWOLONE — to klasyczne użycie solvera do nauki. Granica: review własnych rąk po fakcie = OK; podpowiedź w trakcie aktywnej ręki = RTA = zakaz. Dlatego trzymamy projekt po właściwej stronie tej granicy: ręczny upload, brak integracji z klientem GG, brak auto-capture okna gry, świadomie wolne działanie (żeby nie kusiło i nie nadawało się do użycia przy stole).

---

## 1. Kontekst projektu

- Format: **No-Limit Hold'em, turnieje** (rebuy/turbo i standard). Różnica między wariantami sprowadza się głównie do typowych głębokości stacków i struktury ante — sama matematyka push/fold jest identyczna.
- Faza 1 (ten dokument): **silnik preflop push/fold liczony Nash + ICM**. Postflop i warstwa wizji (zdjęcie → stan gry) świadomie odłożone na później (sekcja 8).
- Język: Python (najszybsza droga do działającego silnika; dojrzałe biblioteki).
- Cel jakościowy: **liczby muszą się zgadzać**. Weryfikujemy wynik względem znanych charts i komercyjnych narzędzi (sekcja 7), zanim dołożymy UI.

---

## 2. Zakres Fazy 1

Silnik, który dla zadanego spotu zwraca optymalną decyzję preflop:
- **shove / fold** dla gracza pierwszego do akcji (tzw. first-in),
- **call / fold** dla gracza za szuflem,
- wszystko liczone w przestrzeni **$ICM**, nie tylko w żetonach.

Wejście: liczba graczy, stacki (w BB), pozycje, blindy + ante, struktura wypłat, liczba pozostałych graczy w turnieju, ręka hero (lub liczymy pełne range'e).
Wyjście: range shove / range call dla danego spotu + decyzja dla konkretnej ręki.

Świadomie **poza** Fazą 1: pełne drzewa z mniejszymi raise'ami (min-raise, postflop), multiway powyżej 3-handed na start (dokładamy etapami).

---

## 3. WIEDZA DO ZDOBYCIA + ŹRÓDŁA

Agent ma przeczytać poniższe ZANIM zacznie kodować silnik, i wyciągnąć z każdego źródła konkretne wzory/koncepcje (nie streszczać „o czym jest", tylko wynotować matematykę).

### 3a. Teoria push/fold (shove-or-fold)
- **GTO Wizard — „Short-Stacked Play in MTTs"**: https://blog.gtowizard.com/short-stacked-play-in-mtts/
  Co wyciągnąć: dlaczego przy krótkim stacku (≈ ≤10–15 BB) strategia degeneruje się do all-in/fold i kiedy to przestaje być optymalne.
- **Bill Chen & Jerrod Ankenman — „The Mathematics of Poker"** (rozdziały o grze [0,1] i jam-or-fold).
  Co wyciągnąć: formalne wyprowadzenie EV shove'a i warunki indyferencji w równowadze.
- **System SAGE (Chen & Alspach), „Sit-and-Go Endgame"**: punkt odniesienia dla heads-up jam/fold — dobry do walidacji najprostszego przypadku.

### 3b. Równowaga Nasha dla push/fold
- **Lee Nelson, Tysen Streib, Kim Lee — „Kill Everyone"**: klasyka liczenia equilibrium push/fold w turniejach (Streib robił obliczenia Nasha). Co wyciągnąć: jak konstruować range shove vs range call w równowadze i jak ICM zacieśnia te range'e.
- Pojęcie do opanowania: **iterated best response / fictitious play** — algorytm dochodzenia do Nasha przez naprzemienne liczenie najlepszej odpowiedzi shovera i callera aż do punktu stałego.

### 3c. ICM (Independent Chip Model)
- **GTO Wizard — „ICM Basics"**: https://blog.gtowizard.com/icm-basics/
  ICM zamienia stack żetonowy na wartość pieniężną (udział w puli nagród). Pierwszy raz zastosowany do pokera przez Masona Malmutha w 1987. Model używa samych wielkości stacków, żeby wyznaczyć prawdopodobieństwo zajęcia każdego miejsca, a potem przypisuje equity wg struktury wypłat. W turniejach wartość żetonów NIE skaluje się liniowo — podwojenie stacka nie podwaja jego wartości.
- **GTO Wizard — „When does ICM become significant in MTTs?"**: https://blog.gtowizard.com/when-does-icm-become-significant-in-mtts/
  Ważna korekta pojęciowa: ICM nie zakłada, że turniej się zatrzymuje — to tylko estymacja prawdopodobieństw miejsc; nie uwzględnia pozycji ani rosnących blindów.
- **D.A. Harville (1973), „Assigning Probabilities to the Outcomes of Multi-Entry Competitions", JASA**: oryginalna matematyka stojąca za modelem Malmuth–Harville (prawdopodobieństwa miejsc proporcjonalne do stacków). To jest dokładny wzór, który implementujemy.

### 3d. Risk premium / bubble factor (efekt ICM na decyzje)
- **GTO Wizard — „ICM Basics"** (ta sama strona, sekcja o risk premium): marginalnie +cEV spot bywa −$EV w turnieju; przy dużych pay-jumpach wszyscy poza największymi stackami zacieśniają.
- Kluczowa implikacja do kodu: **nie liczymy osobnego „risk premium" jako magicznej liczby — on wychodzi sam**, jeśli EV liczymy w dolarach ICM (a nie w żetonach). Risk premium to tylko nazwa zjawiska, że przegrana tych samych żetonów kosztuje więcej $ niż wygrana ich daje.

---

## 4. NARZĘDZIA / BIBLIOTEKI (open-source, zweryfikowane)

- **PokerKit** (`pip install pokerkit`, repo `uoftcprg/pokerkit`, licencja MIT, Python 3.11+): symulacja gry + ewaluacja rąk + **gotowa funkcja `pokerkit.analysis.calculate_icm`**. To nasz domyślny silnik ICM i ewaluator. https://github.com/uoftcprg/pokerkit
- **eval7** (`pip install eval7`): szybka ewaluacja rąk, przybliżone liczenie equity dla range'ów i **parser stringów range'ów w stylu PokerStove** (np. `"AJ+, ATs, KQ+, 33-JJ"`). Idealne do equity all-in preflop. https://pypi.org/project/eval7
- **Benchmark poprawności (komercyjne, używamy tylko jako wzorzec wyników):** HoldemResources Calculator (HRC) oraz ICMIZER — branżowy standard dla Nash push/fold + ICM. Nie integrujemy ich; porównujemy do nich nasze liczby ręcznie na kilku spotach.

> Uwaga dla agenta: zanim założysz, że dana funkcja/wersja biblioteki istnieje — sprawdź aktualną wersję na PyPI/GitHub. API PokerKit zmieniało się między wersjami.

---

## 5. ARCHITEKTURA FAZY 1

```
[ Spot input ]  -> stacki(BB), pozycje, blindy+ante, payouts, #remaining, ręka hero
        |
        v
[ Equity engine ]      eval7 / PokerKit: range-vs-range all-in equity
        |
        v
[ ICM engine ]         PokerKit.calculate_icm (lub własny Malmuth-Harville): stacki -> $equity
        |
        v
[ Push/fold solver ]   iterated best response (fictitious play) w przestrzeni $ICM
        |               -> range shove / range call / decyzja dla ręki hero
        v
[ Output / CLI ]       na start zwykły CLI/JSON; UI dopiero po walidacji liczb
```

Rdzeń solvera (HU, do uogólnienia później):
1. Zainicjuj range shove SB i range call BB.
2. Powtarzaj do punktu stałego:
   - przy danym range call BB policz najlepszy range shove SB (shove ⟺ $EV_shove > $EV_fold dla danej ręki),
   - przy danym range shove SB policz najlepszy range call BB (call ⟺ $EV_call > $EV_fold).
3. `$EV_shove(ręka) = P(BB foldzi)·$ICM(stack po zgarnięciu blindów) + P(BB calluje)·[equity·$ICM(wygrana) + (1−equity)·$ICM(przegrana)]`.
   Wszystkie wyniki terminalne wyceniane przez ICM, nie w żetonach.

---

## 6. PLAN DZIAŁANIA (milestones)

- **M0 — setup:** repo, venv, `pokerkit` + `eval7`, smoke test (ocena jednej ręki, jeden ICM dla przykładowych stacków).
- **M1 — equity engine:** range-vs-range all-in equity. *Walidacja:* AKo vs QQ ≈ 43/57, AKs vs 22 ≈ 50/50 (znane matchupy).
- **M2 — HU chip-EV push/fold:** solver Nash bez ICM. *Walidacja:* odtworzenie publikowanych charts HU Nash push/fold (np. SAGE) z dokładnością do pojedynczych rąk granicznych.
- **M3 — ICM engine:** `calculate_icm`. *Walidacja:* equity ICM dla 3–4 graczy zgodne z ręcznym Malmuth–Harville i z HRC na 2–3 spotach.
- **M4 — push/fold pod ICM:** EV liczone w $ICM. *Walidacja:* range'e zacieśniają się względem cEV w spotach bańkowych (zgodnie kierunkowo z HRC/ICMIZER).
- **M5 — multiway:** 3-handed, potem first-in vs całe pozostałe pozycje przy pełnym stole.
- **M6 — wejście spotu + CLI/JSON output:** prosty interfejs do wpisania spotu i odczytu decyzji.

---

## 7. KRYTERIA AKCEPTACJI

- Każdy milestone ma walidację liczbową **zanim** ruszymy dalej (patrz M1–M4).
- Dla 5 wybranych spotów (różne głębokości stacka i etapy turnieju) nasze range'e shove/call porównujemy ręcznie z HRC lub ICMIZER. Rozbieżności na rękach granicznych są dopuszczalne, ale kierunek i trzon range'a muszą się zgadzać.
- Equity all-in z naszego enginu vs niezależny kalkulator (np. equity z PokerKit vs eval7) — różnica < 0.5%.
- **Zero „wymyślania" liczb przez LLM.** Decyzje liczy deterministyczny silnik; rola modelu (jeśli w ogóle w Fazie 1) to tylko opis wyniku po polsku, nigdy samo liczenie.

---

## 8. CO ŚWIADOMIE ODKŁADAMY (kolejne fazy)

- **Postflop:** wymaga prawdziwego silnika CFR (np. własna implementacja albo open-source TexasSolver). LLM tego nie policzy.
- **Tłumaczenie wyników na ludzki język** (Haiku): „shovasz tu QJs bo masz fold equity X i risk premium Y" — warstwa edukacyjna na bazie liczb z silnika.

---

## 9. FUNKCJA: Analiza rozdania (review po zdjęciu)

Cel: wrzucasz zdjęcie **zakończonego** rozdania, narzędzie odtwarza spot i pokazuje optymalną decyzję, żebyś wiedział czy zagrałeś dobrze, źle, albo co poprawić. To review do nauki — NIE podpowiadacz na żywo (patrz sekcja 0).

Pipeline (etapami):
1. **Obszar uploadu (już w prototypie strony):** dropzone + podgląd wczytanego obrazu (PNG/JPG/JPEG/WEBP), ręczny upload.
2. **Parser obrazu (później, Haiku vision):** zdjęcie → ustrukturyzowany stan: pozycje, stacki w BB, blindy/ante, karty hero, akcja przed hero, etap turnieju. To jedyna rola modelu tutaj — czytanie obrazu, NIE liczenie decyzji.
3. **Silnik Nash/ICM (z Faz 1):** liczy spot na podstawie sparsowanego stanu → rekomendacja: push/fold, a w głębszych spotach raise z sizingiem (small/mid/big).
4. **Werdykt:** porównanie decyzji gracza z rekomendacją + krótki komentarz „OK / błąd / co poprawić".

Granice (twarde):
- Tylko ręczny upload zrzutów po fakcie. Zero integracji z klientem GG, zero nasłuchu/auto-capture aktywnego stołu.
- Wolne działanie jest akceptowalne i wręcz pożądane — to narzędzie do review, nie do gry.
- Sizing raise (small/mid/big) ma sens dopiero, gdy dołożymy drzewo z raise'ami / postflop; dla czystego preflop push/fold output to shove/fold. Do tego czasu w UI sloty small/mid/big zostają jako placeholdery.

---

## PIERWSZE ZADANIE DLA AGENTA

1. Załóż repo i środowisko, zainstaluj `pokerkit` i `eval7`, potwierdź wersje z PyPI.
2. Napisz dwa smoke testy: (a) equity AKo vs QQ, (b) `calculate_icm` dla stacków [5000, 3000, 2000] przy wypłatach [50, 30, 20].
3. Przeczytaj źródła z sekcji 3 i wynotuj wzory EV_shove / EV_call oraz wzór Malmuth–Harville do `NOTES_theory.md`.
4. Dopiero potem przejdź do M1. Nie pisz UI, dopóki M1–M4 nie przejdą walidacji.
