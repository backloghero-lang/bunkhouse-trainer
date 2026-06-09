# NOTES_theory.md — matematyka silnika push/fold (Faza 1)

> Wynotowana matematyka ze zrodel z HANDOFF sekcja 3. Nie streszczenia — wzory.
> Kazda liczba w projekcie wychodzi z tych wzorow policzonych deterministycznie,
> nigdy "z glowy" modelu (HANDOFF sekcja 7).

---

## 1. ICM — model Malmuth–Harville (Harville 1973; Malmuth 1987)

Dane: stacki zetonowe `s_1..s_n`, suma `S = Σ s_i`; struktura wyplat `payout[1..k]`
(payout[1] = 1. miejsce). Zalozenie modelu: **prawdopodobienstwo zajecia kolejnego
miejsca jest proporcjonalne do udzialu w pozostalych zetonach** (model bez pozycji,
bez blindow, bez skillu — tylko stacki).

**Prawdopodobienstwo 1. miejsca:**

    P(i konczy 1.) = s_i / S

**Prawdopodobienstwo konkretnej pelnej kolejnosci** `(i_1 > i_2 > ... > i_n)`:

    P(kolejnosci) = Π_{m=1..n}  s_{i_m} / ( Σ_{t=m..n} s_{i_t} )

tj. po "usunieciu" zwyciezcy liczymy 2. miejsce proporcjonalnie do stackow
pozostalych graczy, itd. (warunkowo, bez zwracania).

**$equity gracza i** = suma po platnych pozycjach `p` z prawdopodobienstwa, ze i
konczy na pozycji p, razy nagroda:

    $EQ_i = Σ_{p=1..k}  P(i konczy na miejscu p) · payout[p]

Niezmiennik kontrolny:  `Σ_i $EQ_i = Σ_p payout[p]` (cala pula sie rozdaje).

Implementacja: `pushfold/icm.py :: calculate_icm` — rekurencja rozdajaca kolejne
platne miejsca, ciecie po ostatniej niezerowej nagrodzie. pokerkit.calculate_icm
liczy ten sam model (cross-check w `calculate_icm_crosscheck`, aktywny na Py>=3.11).

**Walidacja reczna (smoke test b)** — stacki [5000,3000,2000], payouts [50,30,20], S=10000:

| gracz | P(1.) | P(2.) | P(3.) | $EQ = 50·P1+30·P2+20·P3 |
|-------|-------|-------|-------|--------------------------|
| A 5000| 0.5000| 0.33929| 0.16071| **38.3929** |
| B 3000| 0.3000| 0.37500| 0.32500| **32.7500** |
| C 2000| 0.2000| 0.28571| 0.51429| **28.8571** |
|       |       |       |       | suma = **100.00** ✓ |

P(2.) wyliczone warunkowo, np. P(A 2.) = P(B 1.)·s_A/(s_A+s_C) + P(C 1.)·s_A/(s_A+s_B)
= 0.3·(5000/7000) + 0.2·(5000/8000) = 0.33929. Zgodne z outputem `calculate_icm`.

---

## 2. EV shove / EV call w przestrzeni $ICM (HANDOFF sekcja 5)

Liczymy w DOLARACH ICM (udzial w puli), nie w zetonach. Risk premium / bubble factor
NIE jest osobna magiczna liczba — wychodzi sam, bo przegrana tych samych zetonow
kosztuje wiecej $ niz wygrana ich daje (HANDOFF 3d).

Oznaczenia dla spotu HU (SB = shover, BB = caller), efektywny stack `E` (BB),
blind `b`, ante `a`; `ICM($)` wycenia stan po danym wyniku przez model z sekcji 1.

**EV shove'a danej reki h** (SB rozwaza all-in):

    $EV_shove(h) =   P(BB folduje) · ICM( stack_SB + zgarniete blindy/ante )
                   + P(BB calluje) · [  eq(h | range_call) · ICM( stack po wygranej )
                                      + (1 − eq(h | range_call)) · ICM( stack po przegranej ) ]

gdzie `eq(h | range_call)` = equity all-in reki h przeciw range'owi z jakim BB calluje
(liczone enginem z `equity.py`). `P(BB folduje) = 1 − P(BB calluje)`, a `P(BB calluje)`
= udzial range'a call w 1326 kombinacjach (minus karty hero jako dead).

**Warunek shove'a (best response SB):**

    shove h  ⟺  $EV_shove(h) > $EV_fold(h)

gdzie `$EV_fold(h) = ICM( stack_SB − wlozony do puli SB blind )` (stan po oddaniu reki).

**EV calla danej reki h przez BB** (po tym jak SB poszedl all-in):

    $EV_call(h) =   eq(h | range_shove) · ICM( stack BB po wygranej )
                  + (1 − eq(h | range_shove)) · ICM( stack BB po przegranej )

    $EV_fold_BB    = ICM( stack BB − wplacony blind )

**Warunek calla (best response BB):**

    call h  ⟺  $EV_call(h) > $EV_fold_BB

Wszystkie stany terminalne wyceniane przez ICM (sekcja 1), nie w zetonach.

---

## 3. Nash push/fold = iterated best response / fictitious play

Range'y shove (SB) i call (BB) to wzajemne najlepsze odpowiedzi. Punkt staly:

1. Zainicjuj `range_call_BB` (np. pusty lub szeroki).
2. Powtarzaj do zbieznosci:
   a. dla biezacego `range_call_BB` policz `range_shove_SB` = { h : $EV_shove(h) > $EV_fold(h) },
   b. dla biezacego `range_shove_SB` policz `range_call_BB`  = { h : $EV_call(h) > $EV_fold_BB }.
3. Stop, gdy range'y przestaja sie zmieniac (lub max(|Δ$EV|) < eps na rekach granicznych).

W cEV (bez ICM) -> klasyczne charty Nash push/fold (walidacja M2 wzgledem SAGE).
W $ICM -> range'y sie ZACIESNIAJA przy duzych pay-jumpach (walidacja M4 kierunkowo
wzgledem HRC/ICMIZER). To jest "risk premium" bez liczenia go osobno (sekcja 2).

System SAGE (Chen–Alspach) — zamknieta heurystyka HU jam/fold (Power Index z rangi
i sufitu pary/suited), uzyteczna jako tani punkt odniesienia dla najprostszego
przypadku HU (walidacja M2).

---

## Zrodla (HANDOFF sekcja 3)
- GTO Wizard — ICM Basics; When does ICM become significant in MTTs; Short-Stacked Play in MTTs.
- D.A. Harville (1973), "Assigning Probabilities to the Outcomes of Multi-Entry Competitions", JASA.
- Bill Chen & Jerrod Ankenman, "The Mathematics of Poker" (gra [0,1], jam-or-fold).
- Lee Nelson, Tysen Streib, Kim Lee, "Kill Everyone" (Nash push/fold + ICM).
- Chen & Alspach, system SAGE (HU jam/fold).
