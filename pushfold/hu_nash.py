"""Heads-up chip-EV Nash push/fold solver (M2) — fictitious play / iterated best response.

Bez ICM (czysty cEV w zetonach). SB (button) = shove/fold, BB = call/fold.
Equity z prekomputowanej macierzy klasa-vs-klasa (pushfold/data/eq_matrix_v2.json).

Model EV (efektywny stack E w BB, blind SB=sb, BB=bb, bez ante):
  SB shove:  EV = f*(E+bb) + c*(eq_vs_call * 2E)      # f=P(BB fold), c=1-f
  SB fold:   EV = E - sb
  shove  <=>  EV_shove > EV_fold
  BB call:   EV = eq_vs_shove * 2E ;  BB fold: EV = E - bb
  call   <=>  eq_vs_shove > (E - bb) / (2E)
"""
from __future__ import annotations
import json, os
from pushfold.handclasses import canonical_169, combos, TOTAL_COMBOS

CLASSES = canonical_169()
_IDX = {c: k for k, c in enumerate(CLASSES)}
_COMBOS = [combos(c) for c in CLASSES]
_MATRIX_PATH = os.path.join(os.path.dirname(__file__), "data", "eq_matrix_v2.json")
_M = json.load(open(_MATRIX_PATH))

import numpy as np
_MA = np.array(_M, dtype=float)                      # 169x169 equity
_CW = np.array(_COMBOS, dtype=float)                 # wektor liczby kombinacji


def _eq_vs_weighted(i: int, freq: list[float]) -> float:
    """Equity klasy i vs range jako MIESZANA strategia (freq[j] in [0,1]),
    wazona liczba kombinacji."""
    num = den = 0.0
    row = _M[i]
    for j, fr in enumerate(freq):
        if fr > 0.0:
            w = _COMBOS[j] * fr
            num += row[j] * w
            den += w
    return num / den if den else 0.0


def _calls_frac(freq: list[float]) -> float:
    return sum(_COMBOS[j] * freq[j] for j in range(169)) / TOTAL_COMBOS


def solve_hu_nash_cev(E: float, sb: float = 0.5, bb: float = 1.0,
                      iters: int = 300):
    """Nash push/fold cEV przez USREDNIONE fictitious play (zbiezne, bez oscylacji).

    Zwraca (sb_shove_set, bb_call_set): klasy, ktore w rownowadze sa shove/call
    z czestoscia > 0.5 (push/fold jest niemal czysty; progra hands graniczne).
    """
    ev_fold_sb = E - sb
    bb_thr = (E - bb) / (2 * E)

    sb_sum = np.zeros(169); bb_sum = np.zeros(169)
    sb_avg = np.ones(169); bb_avg = np.ones(169)

    def eq_all(freq):
        w = _CW * freq
        den = w.sum()
        return (_MA @ w) / den if den > 0 else np.zeros(169)

    for t in range(1, iters + 1):
        # BB best response vs sredni shove SB
        br_bb = (eq_all(sb_avg) > bb_thr).astype(float)
        # SB best response vs sredni call BB
        c = float((_CW * bb_avg).sum()) / TOTAL_COMBOS
        f = 1.0 - c
        if c > 0:
            ev = f * (E + bb) + c * (eq_all(bb_avg) * 2 * E)
        else:
            ev = np.full(169, E + bb)
        br_sb = (ev > ev_fold_sb).astype(float)
        sb_sum += br_sb; bb_sum += br_bb
        sb_avg = sb_sum / t; bb_avg = bb_sum / t

    sset = [CLASSES[i] for i in range(169) if sb_avg[i] > 0.5]
    cset = [CLASSES[i] for i in range(169) if bb_avg[i] > 0.5]
    return sset, cset


def range_pct(classes) -> float:
    return 100.0 * sum(combos(c) for c in classes) / TOTAL_COMBOS


def grid(selected) -> str:
    """13x13 siatka: X=w range, .=poza."""
    sel = set(selected)
    R = "AKQJT98765432"
    out = []
    for i, hi in enumerate(R):
        line = []
        for j, lo in enumerate(R):
            if i == j: cls = hi + lo
            elif i < j: cls = hi + lo + "s"
            else: cls = lo + hi + "o"
            line.append("X" if cls in sel else ".")
        out.append(" ".join(line))
    return "\n".join(out)


if __name__ == "__main__":
    for E in (10.0, 15.0):
        s, c = solve_hu_nash_cev(E)
        print(f"\n=== E={E}bb ===  SB shove {range_pct(s):.1f}%   BB call {range_pct(c):.1f}%  (BB thr eq>{(E-1)/(2*E):.3f})")
        print("SB shove:\n" + grid(s))
        print("BB call:\n" + grid(c))
