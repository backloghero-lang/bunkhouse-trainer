"""M5a — equity N-way all-in (>=2 graczy) przez seeded Monte Carlo.

Macierz 2-way (M2) nie wystarcza do potow 3-way+, gdzie trzeba ocenic wszystkich
naraz i dzielic split-poty. Tu liczymy equity kazdego gracza w all-inie wielostronnym.
Deterministyczne (ustalony seed). Gracze podani jako konkretne reki (po 2 karty) lub
range'e (string PokerStove); reszta talii losowana.
"""
from __future__ import annotations
import random
import eval7

_FULL = [r + s for r in "23456789TJQKA" for s in "shdc"]
_DECK = [eval7.Card(c) for c in _FULL]
_IDX = {str(c): k for k, c in enumerate(_DECK)}
_R52 = range(52)


def _combos(spec: str):
    """spec: '2 karty' (np. 'As Kd') lub range PokerStove -> lista par indeksow kart."""
    parts = spec.split()
    if len(parts) == 2 and all(len(p) == 2 for p in parts):
        return [(_IDX[parts[0]], _IDX[parts[1]])]
    return [(_IDX[str(c1)], _IDX[str(c2)]) for (c1, c2), _w in eval7.HandRange(spec).hands]


def multiway_equity(specs, board="", iterations=20000, seed=1234):
    """Equity kazdego gracza w all-inie N-way. Zwraca liste (sumuje sie do 1)."""
    players = [_combos(s) for s in specs]
    n = len(players)
    board_idx = [_IDX[c] for c in board.split()] if board else []
    need = 5 - len(board_idx)
    rng = random.Random(seed)
    eq = [0.0] * n
    D = _DECK
    done = 0
    while done < iterations:
        used = set(board_idx)
        hole = []
        ok = True
        for combos in players:
            a, b = rng.choice(combos)
            if a in used or b in used:
                ok = False; break
            used.add(a); used.add(b); hole.append((a, b))
        if not ok:
            continue
        bd = rng.sample(_R52, 5 + 0) if not board_idx else None
        if board_idx:
            extra = []
            while len(extra) < need:
                k = rng.randrange(52)
                if k not in used and k not in extra:
                    extra.append(k)
            board_full = board_idx + extra
        else:
            board_full = []
            while len(board_full) < 5:
                k = rng.randrange(52)
                if k not in used and k not in board_full:
                    board_full.append(k)
        bcards = [D[k] for k in board_full]
        scores = [eval7.evaluate([D[a], D[b]] + bcards) for (a, b) in hole]
        best = max(scores)
        winners = [i for i, sc in enumerate(scores) if sc == best]
        share = 1.0 / len(winners)
        for i in winners:
            eq[i] += share
        done += 1
    return [e / iterations for e in eq]
