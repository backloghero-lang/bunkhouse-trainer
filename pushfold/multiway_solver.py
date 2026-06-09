"""M5b/M5c — first-in push/fold solver (model NIEZALEZNYCH callerow), cEV.

Hero open-shove (E w BB) vs lista graczy z tylu (kazdy: blind + range calla).
Caller decyduje HU vs shove (niezaleznie). EV hero sumuje podzbiory callerow:
0 -> wygrana blindow, 1 -> equity 2-way (macierz), >=2 -> proxy 2-way vs polaczony range
(szybko, samospojnie). `max_callers` ucina rzadkie poty 3+ przy pelnym stole.
Redukuje sie DOKLADNIE do M2 przy 1 graczu z tylu.
"""
from __future__ import annotations
from itertools import combinations
import numpy as np
from pushfold.handclasses import canonical_169, combos as cls_combos, representative, TOTAL_COMBOS
from pushfold.hu_nash import _MA, _CW
from pushfold.multiway_equity import multiway_equity

CLASSES = canonical_169()
_REPR = [" ".join(representative(c)) for c in CLASSES]


def _eq_vs_mask(mask):
    w = _CW * mask
    den = w.sum()
    return (_MA @ w) / den if den > 0 else np.zeros(169)


def _range_str(s):
    return ",".join(s) if s else ""


def _hero_ev(E, behind_blinds, hero_blind, c, call_avg, max_callers):
    nb = len(behind_blinds)
    eq1 = [_eq_vs_mask(call_avg[i]) for i in range(nb)]
    ev = np.zeros(169)
    upper = min(nb, max_callers)
    pmass = 0.0
    for r in range(upper + 1):
        for S in combinations(range(nb), r):
            p = 1.0
            for i in range(nb):
                p *= c[i] if i in S else (1 - c[i])
            if p <= 0:
                continue
            pmass += p
            pot = (len(S) + 1) * E + sum(behind_blinds[j] for j in range(nb) if j not in S)
            if len(S) == 0:
                eqv = np.ones(169)
            elif len(S) == 1:
                eqv = eq1[S[0]]
            else:
                combined = np.clip(sum(call_avg[j] for j in S), 0.0, 1.0)
                eqv = _eq_vs_mask(combined)
            ev = ev + p * pot * eqv
    if pmass > 0:
        ev = ev / pmass
    return ev


def solve_firstin_cev(E, behind_blinds, hero_blind=0.5, iters=300, max_callers=2):
    """Zwraca (hero_shove_set, [call_set_per_behind])."""
    nb = len(behind_blinds)
    total_behind = sum(behind_blinds)
    thr = [(E - behind_blinds[i]) / (2 * E + (total_behind - behind_blinds[i])) for i in range(nb)]

    hero_sum = np.zeros(169); hero_avg = np.ones(169)
    call_sum = [np.zeros(169) for _ in range(nb)]
    call_avg = [np.ones(169) for _ in range(nb)]

    for t in range(1, iters + 1):
        eq_vs_hero = _eq_vs_mask(hero_avg)
        br_calls = [(eq_vs_hero > thr[i]).astype(float) for i in range(nb)]
        c = [float((_CW * call_avg[i]).sum()) / TOTAL_COMBOS for i in range(nb)]
        ev = _hero_ev(E, behind_blinds, hero_blind, c, call_avg, max_callers)
        br_hero = (ev > (E - hero_blind)).astype(float)
        hero_sum += br_hero; hero_avg = hero_sum / t
        for i in range(nb):
            call_sum[i] += br_calls[i]; call_avg[i] = call_sum[i] / t

    call_sets = [{CLASSES[k] for k in range(169) if call_avg[i][k] > 0.5} for i in range(nb)]
    hero_set = [CLASSES[i] for i in range(169) if hero_avg[i] > 0.5]
    return hero_set, call_sets


def true_multiway_equity_vector(caller_sets, mw_iters=1000, seed=99):
    """Pomocniczo (analiza/M5c+): prawdziwe equity multiway (MC) klasy-reprezentanta
    vs zbiory range'ow callerow. Do mierzenia bledu proxy."""
    strs = [_range_str(s) for s in caller_sets]
    out = np.zeros(169)
    for i in range(169):
        out[i] = multiway_equity([_REPR[i]] + strs, iterations=mw_iters, seed=seed)[0]
    return out


def range_pct(classes):
    return 100.0 * sum(cls_combos(c) for c in classes) / TOTAL_COMBOS
