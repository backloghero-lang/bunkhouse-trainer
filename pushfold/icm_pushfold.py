"""M4 — push/fold pod ICM. Stany terminalne wyceniane w $ICM (nie w zetonach).

Spot: N graczy (stacki w BB), wyplaty, blindy. SB (first-in) shove/fold, BB call/fold,
reszta foldzi (stacki staja). ICM 4 stanow terminalnych NIE zalezy od reki -> liczony RAZ,
potem usrednione fictitious play tak szybkie jak M2. Risk premium wychodzi sam (HANDOFF 3d).
"""
from __future__ import annotations
import numpy as np
from pushfold.icm import calculate_icm
from pushfold.handclasses import canonical_169, combos, TOTAL_COMBOS
from pushfold.hu_nash import _MA, _CW

CLASSES = canonical_169()


def _terminals(stacks, payouts, sb_i, bb_i, sb, bb):
    E = min(stacks[sb_i], stacks[bb_i])

    def mod(delta):
        s = list(stacks)
        for idx, d in delta.items():
            s[idx] += d
        return s

    foldSB  = calculate_icm(mod({sb_i: -sb, bb_i: +sb}), payouts)
    BBfold  = calculate_icm(mod({sb_i: +bb, bb_i: -bb}), payouts)
    SBwins  = calculate_icm(mod({sb_i: +E,  bb_i: -E}),  payouts)
    SBloses = calculate_icm(mod({sb_i: -E,  bb_i: +E}),  payouts)
    return {"F_sb": foldSB[sb_i], "A_sb": BBfold[sb_i], "W_sb": SBwins[sb_i],
            "L_sb": SBloses[sb_i], "G_bb": BBfold[bb_i], "W_bb": SBloses[bb_i],
            "L_bb": SBwins[bb_i]}


def _eq_all(freq):
    w = _CW * freq
    den = w.sum()
    return (_MA @ w) / den if den > 0 else np.zeros(169)


def solve_pushfold_icm(stacks, payouts, sb_i=0, bb_i=1, sb=0.5, bb=1.0, iters=300):
    t = _terminals(stacks, payouts, sb_i, bb_i, sb, bb)
    F, A, W, L = t["F_sb"], t["A_sb"], t["W_sb"], t["L_sb"]
    Gb, Wb, Lb = t["G_bb"], t["W_bb"], t["L_bb"]
    sb_sum = np.zeros(169); bb_sum = np.zeros(169)
    sb_avg = np.ones(169);  bb_avg = np.ones(169)
    for it in range(1, iters + 1):
        eqb = _eq_all(sb_avg)
        br_bb = (eqb * Wb + (1 - eqb) * Lb > Gb).astype(float)
        c = float((_CW * bb_avg).sum()) / TOTAL_COMBOS
        f = 1.0 - c
        eqs = _eq_all(bb_avg)
        br_sb = (f * A + c * (eqs * W + (1 - eqs) * L) > F).astype(float)
        sb_sum += br_sb; bb_sum += br_bb
        sb_avg = sb_sum / it; bb_avg = bb_sum / it
    sset = [CLASSES[i] for i in range(169) if sb_avg[i] > 0.5]
    cset = [CLASSES[i] for i in range(169) if bb_avg[i] > 0.5]
    return sset, cset


def bb_call_threshold(stacks, payouts, sb_i=0, bb_i=1, sb=0.5, bb=1.0):
    """Analityczny prog equity calla BB: eq > (Gb-Lb)/(Wb-Lb)."""
    t = _terminals(stacks, payouts, sb_i, bb_i, sb, bb)
    return (t["G_bb"] - t["L_bb"]) / (t["W_bb"] - t["L_bb"])


def range_pct(classes):
    return 100.0 * sum(combos(c) for c in classes) / TOTAL_COMBOS
