"""All-in preflop equity engine (eval7).

Decyzja projektowa: eval7 jako ewaluator (szybki C-owy `evaluate`) + parser range'ow
w stylu PokerStove (`HandRange`). Liczenie equity robimy WLASNE i deterministyczne:
  - hand-vs-hand i male range'y: EXACT enumeration plansz,
  - wieksze range'y / szybkosc dla solvera: Monte Carlo z USTALONYM ziarnem (powtarzalne).

Uwaga: `eval7.py_hand_vs_range_exact` w 0.1.10 zwraca bledne wyniki dla pustej planszy
(znany bug) — dlatego liczymy equity samodzielnie na bazie `eval7.evaluate`.

Stabilizacja (M1-hardening): talia kart cache'owana raz (bez odtwarzania obiektow Card
w kazdej iteracji MC), twarda walidacja wejscia, respektowanie wag HandRange.
"""
from __future__ import annotations

import itertools
import random
from typing import Sequence

import eval7

RANKS = "23456789TJQKA"
SUITS = "shdc"
FULL_DECK = [r + s for r in RANKS for s in SUITS]

# --- cache: obiekty Card budowane RAZ (kluczowe dla wydajnosci MC) ---
_DECK_OBJS: list[eval7.Card] = [eval7.Card(c) for c in FULL_DECK]
_CARD_BY_STR: dict[str, eval7.Card] = {str(c): c for c in _DECK_OBJS}
_VALID = set(_CARD_BY_STR)


def _card(spec: str) -> eval7.Card:
    try:
        return _CARD_BY_STR[spec]
    except KeyError:
        raise ValueError(f"nieprawidlowa karta: {spec!r} (oczekiwany format np. 'As','Kd','Th')")


def _cards(specs: Sequence[str]) -> list[eval7.Card]:
    return [_card(s) for s in specs]


def _deck_excluding(dead: set[str]) -> list[eval7.Card]:
    return [c for c in _DECK_OBJS if str(c) not in dead]


def _check_no_dupes(*groups: Sequence[str]) -> set[str]:
    seen: set[str] = set()
    for g in groups:
        for s in g:
            if s not in _VALID:
                raise ValueError(f"nieprawidlowa karta: {s!r}")
            if s in seen:
                raise ValueError(f"zduplikowana karta w wejsciu: {s!r}")
            seen.add(s)
    return seen


# --------------------------------------------------------------------------- #
# hand vs hand — EXACT (deterministyczny wzorzec)
# --------------------------------------------------------------------------- #
def hand_vs_hand_equity(hero: Sequence[str], villain: Sequence[str],
                        board: Sequence[str] = ()) -> float:
    """Exact equity hero vs konkretna reka villaina przez pelne wyliczenie plansz."""
    if len(hero) != 2 or len(villain) != 2:
        raise ValueError("hero i villain musza miec dokladnie po 2 karty")
    if len(board) > 5:
        raise ValueError("plansza moze miec maksymalnie 5 kart")
    dead = _check_no_dupes(hero, villain, board)
    hero_c, vill_c, board_c = _cards(hero), _cards(villain), _cards(board)
    deck = _deck_excluding(dead)
    need = 5 - len(board_c)

    win = tie = total = 0
    for extra in itertools.combinations(deck, need):
        full = board_c + list(extra)
        hv = eval7.evaluate(hero_c + full)
        vv = eval7.evaluate(vill_c + full)
        if hv > vv:
            win += 1
        elif hv == vv:
            tie += 1
        total += 1
    return (win + tie / 2) / total


# --------------------------------------------------------------------------- #
# range helpers (z wagami)
# --------------------------------------------------------------------------- #
def range_string_to_weighted_combos(range_str: str):
    """String range'a PokerStove -> [((Card,Card), weight), ...] (wagi z HandRange)."""
    return [((c1, c2), w) for (c1, c2), w in eval7.HandRange(range_str).hands]


def range_string_to_combos(range_str: str):
    """Jak wyzej, ale bez wag (zgodnosc wsteczna)."""
    return [hand for hand, _w in range_string_to_weighted_combos(range_str)]


def _weighted_no_conflict(range_str: str, dead: set[str]):
    out = []
    for (c1, c2), w in range_string_to_weighted_combos(range_str):
        s1, s2 = str(c1), str(c2)
        if s1 in dead or s2 in dead or s1 == s2 or w <= 0:
            continue
        out.append(((c1, c2), w))
    return out


# --------------------------------------------------------------------------- #
# hand vs range — EXACT lub seeded Monte Carlo (wazone)
# --------------------------------------------------------------------------- #
def hand_vs_range_equity(hero: Sequence[str], villain_range: str,
                         board: Sequence[str] = (), *, exact: bool = False,
                         iterations: int = 100_000, seed: int = 1234) -> float:
    """Equity hero przeciw range'owi villaina (all-in), z uwzglednieniem wag range'a.

    exact=True  -> wazona srednia exact hand-vs-hand po niekonfliktowych kombinacjach.
    exact=False -> wlasny Monte Carlo z ustalonym `seed` (deterministyczny, szybki).
    """
    if len(hero) != 2:
        raise ValueError("hero musi miec dokladnie 2 karty")
    dead = _check_no_dupes(hero, board)
    hero_c, board_c = _cards(hero), _cards(board)
    combos = _weighted_no_conflict(villain_range, dead)
    if not combos:
        raise ValueError("range villaina pusty po usunieciu konfliktow z reka/plansza hero")

    if exact:
        num = den = 0.0
        for (v1, v2), w in combos:
            num += w * hand_vs_hand_equity(hero, [str(v1), str(v2)], board)
            den += w
        return num / den

    rng = random.Random(seed)
    hands = [h for h, _w in combos]
    weights = [w for _h, w in combos]
    need = 5 - len(board_c)
    score = 0.0
    for _ in range(iterations):
        (v1, v2) = rng.choices(hands, weights=weights, k=1)[0]
        used = dead | {str(v1), str(v2)}
        deck = _deck_excluding(used)
        full = board_c + rng.sample(deck, need)
        hv = eval7.evaluate(hero_c + full)
        vv = eval7.evaluate([v1, v2] + full)
        if hv > vv:
            score += 1.0
        elif hv == vv:
            score += 0.5
    return score / iterations


# --------------------------------------------------------------------------- #
# range vs range — wazona srednia po rekach hero
# --------------------------------------------------------------------------- #
def range_vs_range_equity(hero_range: str, villain_range: str,
                          board: Sequence[str] = (), *, exact: bool = False,
                          iterations: int = 100_000, seed: int = 1234) -> float:
    """Equity range'a hero przeciw range'owi villaina (all-in), wazona srednia po hero."""
    dead = _check_no_dupes(board)
    hero_combos = _weighted_no_conflict(hero_range, dead)
    if not hero_combos:
        raise ValueError("range hero pusty")
    num = den = 0.0
    for (h1, h2), w in hero_combos:
        num += w * hand_vs_range_equity([str(h1), str(h2)], villain_range, board,
                                        exact=exact, iterations=iterations, seed=seed)
        den += w
    return num / den


if __name__ == "__main__":  # smoke
    print("AKo vs QQ (exact):", round(hand_vs_range_equity(["As", "Kd"], "QQ", exact=True) * 100, 2), "%")
