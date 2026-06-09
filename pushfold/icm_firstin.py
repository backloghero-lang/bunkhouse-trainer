"""M7 — first-in open-shove pod ICM (model niezaleznych callerow, rowne stacki E).

Hero open-shove z pozycji vs gracze z tylu; stany terminalne wyceniane w $ICM nad
calym stolem (rowne stacki E zalozone — standard dla chartow). Wartosci ICM stanow
terminalnych to SKALARY per podzbior callerow (nie zaleza od reki), wiec solver jest
tak szybki jak M5c. Redukuje sie do M5c (cEV) przy winner-take-all i do M4 dla HU.
"""
from __future__ import annotations
from itertools import combinations
import numpy as np
from pushfold.handclasses import canonical_169, combos as cls_combos, TOTAL_COMBOS
from pushfold.hu_nash import _MA, _CW
from pushfold.icm import calculate_icm

CLASSES = canonical_169()


def _eq_vs_mask(mask):
    w = _CW * mask
    den = w.sum()
    return (_MA @ w) / den if den > 0 else np.zeros(169)


def _icm_terminals(n_players, payouts, E, hero_i, behind_idx, behind_blinds, hero_blind, max_callers):
    """Zwraca: dict subset->(Vwin,Vlose) dla hero oraz progi callerow (HU ICM)."""
    nb = len(behind_idx)
    base = [E] * n_players
    posted = {hero_i: hero_blind}
    for k, idx in enumerate(behind_idx):
        posted[idx] = behind_blinds[k]

    def icm_hero(stacks):
        return calculate_icm(stacks, payouts)[hero_i]

    def icm_of(stacks, who):
        return calculate_icm(stacks, payouts)[who]

    # hero EV: per podzbior callerow S (indeksy w behind_idx)
    terms = {}
    upper = min(nb, max_callers)
    for r in range(upper + 1):
        for S in combinations(range(nb), r):
            callers = [behind_idx[j] for j in S]
            dead = sum(posted.get(behind_idx[j], 0.0) for j in range(nb) if j not in S)  # blindy folderow z tylu
            dead += posted.get(hero_i, 0.0) if False else 0.0
            # martwe blindy = blindy graczy, ktorzy POSTowali i foldzą (z tylu, nie w S)
            # hero wygrywa: bierze pot = (|S|+1)E + dead; callerzy w S -> 0
            win = list(base)
            win[hero_i] = E + len(S) * E + dead
            for c in callers:
                win[c] = 0
            # uwzglednij ze foldujacy blind-posterzy strac blind
            for j in range(nb):
                if j not in S:
                    idx = behind_idx[j]
                    win[idx] = E - posted.get(idx, 0.0)
            Vwin = icm_of(win, hero_i)
            # hero przegrywa: hero -> 0; jeden caller w S wygrywa pot, reszta S -> 0
            if len(S) == 0:
                Vlose = Vwin  # brak callerow: hero nie moze przegrac (wszyscy foldzą)
            else:
                lose = list(base)
                lose[hero_i] = 0
                winner = callers[0]
                lose[winner] = E + len(S) * E + dead
                for c in callers[1:]:
                    lose[c] = 0
                for j in range(nb):
                    if j not in S:
                        idx = behind_idx[j]
                        lose[idx] = E - posted.get(idx, 0.0)
                Vlose = icm_of(lose, hero_i)
            terms[S] = (Vwin, Vlose)

    # progi callerow (HU ICM vs shove): call <=> eq > (Gi - Li)/(Wi - Li)
    thr = []
    for k, ci in enumerate(behind_idx):
        # caller wygrywa HU (reszta fold): caller=2E+dead_others; hero=0
        dead_o = sum(posted.get(behind_idx[j], 0.0) for j in range(nb) if j != k) + posted.get(hero_i, 0.0)
        win = list(base); win[ci] = 2 * E + dead_o; win[hero_i] = 0
        for j in range(nb):
            if j != k:
                win[behind_idx[j]] = E - posted.get(behind_idx[j], 0.0)
        Wi = icm_of(win, ci)
        lose = list(base); lose[ci] = 0; lose[hero_i] = 2 * E + dead_o
        for j in range(nb):
            if j != k:
                lose[behind_idx[j]] = E - posted.get(behind_idx[j], 0.0)
        Li = icm_of(lose, ci)
        # caller i foldzi -> hero wygrywa nieobciazony pot blindow (zachowanie sumy zetonow):
        # kazdy poster z tylu traci swoj blind, hero zbiera ich sume.
        foldv = list(base)
        for j in range(nb):
            foldv[behind_idx[j]] = E - posted.get(behind_idx[j], 0.0)
        foldv[hero_i] = E - posted.get(hero_i, 0.0) + sum(behind_blinds)
        Gi = icm_of(foldv, ci)
        denom = (Wi - Li)
        thr.append((Gi - Li) / denom if denom != 0 else 1.0)
    return terms, thr


def solve_firstin_icm(E, n_players, payouts, behind_blinds, hero_blind=0.0,
                      hero_i=0, behind_idx=None, iters=250, max_callers=2):
    """Zwraca (hero_shove_set, [call_set_per_behind]) pod ICM (rowne stacki E)."""
    nb = len(behind_blinds)
    if behind_idx is None:
        behind_idx = list(range(1, nb + 1))
    terms, thr = _icm_terminals(n_players, payouts, E, hero_i, behind_idx, behind_blinds,
                                hero_blind, max_callers)
    Vfold = terms[()][0]  # hero foldzi? Nie — to wartosc gdy wszyscy foldza po shove.
    # hero fold (nie shove): hero zachowuje E (minus wlasny blind)
    base = [E] * n_players
    fold_stacks = list(base); fold_stacks[hero_i] = E - hero_blind
    # martwe blindy z tylu po prostu zostaja u posterow w przypadku hero-fold
    hero_fold_val = calculate_icm(fold_stacks, payouts)[hero_i]

    hero_sum = np.zeros(169); hero_avg = np.ones(169)
    call_sum = [np.zeros(169) for _ in range(nb)]
    call_avg = [np.ones(169) for _ in range(nb)]
    for t in range(1, iters + 1):
        eqh = _eq_vs_mask(hero_avg)
        br_calls = [(eqh > thr[i]).astype(float) for i in range(nb)]
        c = [float((_CW * call_avg[i]).sum()) / TOTAL_COMBOS for i in range(nb)]
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
                Vwin, Vlose = terms[S]
                if len(S) == 0:
                    eqv = np.ones(169)
                elif len(S) == 1:
                    eqv = _eq_vs_mask(call_avg[S[0]])
                else:
                    eqv = _eq_vs_mask(np.clip(sum(call_avg[j] for j in S), 0, 1))
                ev = ev + p * (eqv * Vwin + (1 - eqv) * Vlose)
        if pmass > 0:
            ev = ev / pmass
        br_hero = (ev > hero_fold_val).astype(float)
        hero_sum += br_hero; hero_avg = hero_sum / t
        for i in range(nb):
            call_sum[i] += br_calls[i]; call_avg[i] = call_sum[i] / t
    call_sets = [{CLASSES[k] for k in range(169) if call_avg[i][k] > 0.5} for i in range(nb)]
    hero_set = [CLASSES[i] for i in range(169) if hero_avg[i] > 0.5]
    return hero_set, call_sets


def range_pct(classes):
    return 100.0 * sum(cls_combos(c) for c in classes) / TOTAL_COMBOS
