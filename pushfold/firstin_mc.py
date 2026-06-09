"""Hero open-shove range pod model NIEZALEZNYCH callerow, liczony MC z PARTYCYPACJA.

Problem: przy wielu graczach z tylu sumowanie po podzbiorach (z obcieciem) psuje
porzadek pozycyjny. Tu kazda proba losuje, ktorzy gracze z tylu calluja (z czestoscia
c_i, reka z ich range'a), dobiera plansze i liczy udzial hero w potcie — co poprawnie
integruje po WSZYSTKICH licznosciach callerow. Wycena cEV (zetony) lub $ICM.

Range'y callerow bierzemy z taniego solvera FP (zaleza od range'a hero 2-way), a sam
range hero liczymy tym MC. Daje poprawny porzadek: UTG (8 z tylu) ciasniej niz BTN.
"""
from __future__ import annotations
import random
import numpy as np
import eval7
from pushfold.handclasses import canonical_169, combos as cls_combos, representative, TOTAL_COMBOS
from pushfold.icm import calculate_icm

CLASSES = canonical_169()
_FULL = [r + s for r in "23456789TJQKA" for s in "shdc"]
_DECK = [eval7.Card(c) for c in _FULL]
_IDX = {str(c): k for k, c in enumerate(_DECK)}
_REPR_IDX = [tuple(_IDX[x] for x in representative(c)) for c in CLASSES]
_R52 = range(52)


def _range_combo_idx(range_set):
    out = []
    for cls in range_set:
        for (c1, c2), _w in eval7.HandRange(",".join([cls])).hands:
            out.append((_IDX[str(c1)], _IDX[str(c2)]))
    return out


def hero_open_range(E, behind_blinds, caller_sets, caller_freqs, *,
                    n_players=None, payouts=None, hero_i=0, behind_idx=None,
                    hero_blind=0.0, n_mc=2000, seed=11):
    """Zwraca set klas, ktore hero open-shove'uje. cEV gdy payouts is None, inaczej ICM."""
    nb = len(behind_blinds)
    if behind_idx is None:
        behind_idx = list(range(1, nb + 1))
    total_behind = sum(behind_blinds)
    caller_combos = [_range_combo_idx(s) if s else [] for s in caller_sets]
    rng = random.Random(seed)
    D = _DECK

    # ICM terminale (stale) — tylko gdy payouts podane
    icm_cache = {}
    base = [E] * (n_players or (nb + 1))

    fold_val_chips = E - hero_blind
    if payouts is not None:
        fold_stacks = list(base); fold_stacks[hero_i] = E - hero_blind
        fold_val = calculate_icm(fold_stacks, payouts)[hero_i]
    else:
        fold_val = fold_val_chips

    result = []
    for ci, hpair in enumerate(_REPR_IDX):
        h0, h1 = hpair
        acc = 0.0
        done = 0
        while done < n_mc:
            used = {h0, h1}
            sample = []
            sample_cards = []
            ok = True
            for j in range(nb):
                if caller_combos[j] and rng.random() < caller_freqs[j]:
                    a, b = rng.choice(caller_combos[j])
                    if a in used or b in used:
                        ok = False; break
                    used.add(a); used.add(b); sample.append(j); sample_cards.append((a, b))
            if not ok:
                continue
            # plansza
            board = []
            while len(board) < 5:
                k = rng.randrange(52)
                if k not in used and k not in board:
                    board.append(k)
            bcards = [D[k] for k in board]
            if not sample:
                val = (E + total_behind) if payouts is None else _icm_winblinds(
                    icm_cache, base, payouts, hero_i, behind_idx, behind_blinds, nb, E)
                acc += val; done += 1; continue
            hs = eval7.evaluate([D[h0], D[h1]] + bcards)
            best = hs; nbest_hero = True
            opp_scores = []
            for (a, b) in sample_cards:
                sc = eval7.evaluate([D[a], D[b]] + bcards); opp_scores.append(sc)
                if sc > best:
                    best = sc
            winners_hero = (hs == best)
            tie = sum(1 for sc in opp_scores if sc == best) + (1 if hs == best else 0)
            dead = sum(behind_blinds[j] for j in range(nb) if j not in sample)
            if payouts is None:
                pot = (len(sample) + 1) * E + dead
                acc += (pot / tie) if winners_hero else 0.0
            else:
                # ICM: hero wygrywa (udzial 1/tie) -> stack up; inaczej bust
                key = ("w", len(sample))
                acc += _icm_allin(icm_cache, base, payouts, hero_i, sample, behind_idx,
                                  behind_blinds, nb, E, winners_hero, tie)
            done += 1
        ev = acc / n_mc
        if ev > fold_val:
            result.append(CLASSES[ci])
    return result


def _icm_winblinds(cache, base, payouts, hero_i, behind_idx, behind_blinds, nb, E):
    key = "wb"
    if key in cache:
        return cache[key]
    s = list(base)
    s[hero_i] = E + sum(behind_blinds)
    for j in range(nb):
        s[behind_idx[j]] = E - behind_blinds[j]
    v = calculate_icm(s, payouts)[hero_i]
    cache[key] = v
    return v


def _icm_allin(cache, base, payouts, hero_i, sample, behind_idx, behind_blinds, nb, E, hero_win, tie):
    dead = sum(behind_blinds[j] for j in range(nb) if j not in sample)
    pot = (len(sample) + 1) * E + dead
    key = (tuple(sample), hero_win, tie)
    if key in cache:
        return cache[key]
    s = list(base)
    for j in range(nb):
        if j not in sample:
            s[behind_idx[j]] = E - behind_blinds[j]
    callers = [behind_idx[j] for j in sample]
    if hero_win:
        s[hero_i] = pot / tie
        for c in callers:
            s[c] = 0
        if tie > 1:
            share = pot / tie
            for c in callers[:tie - 1]:
                s[c] = share
    else:
        s[hero_i] = 0
        s[callers[0]] = pot
        for c in callers[1:]:
            s[c] = 0
    v = calculate_icm(s, payouts)[hero_i]
    cache[key] = v
    return v


def range_pct(classes):
    return 100.0 * sum(cls_combos(c) for c in classes) / TOTAL_COMBOS
