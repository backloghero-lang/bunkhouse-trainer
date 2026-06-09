"""Buduje 169x169 macierz all-in equity (klasa vs klasa) przez seeded MC.

Poprawnie: losujemy KONKRETNE niekonfliktowe kombinacje obu klas (usrednianie kolorow
+ blokery). Determinizm: komorka (i,j) ma ziarno Random(i*169+j) -> niezalezne od chunkow.
Symetria eq[j][i]=1-eq[i][j]; przekatna 0.5. Zapis po kazdym wierszu (odpornosc na timeout).

Uzycie: python -m pushfold.build_matrix START END
Cache:  pushfold/data/eq_matrix_v2.json
"""
from __future__ import annotations
import json, os, random, sys, eval7
from pushfold.handclasses import canonical_169

N = 1500
CLASSES = canonical_169()
N169 = len(CLASSES)
CACHE = os.path.join(os.path.dirname(__file__), "data", "eq_matrix_v2.json")
_FULL = [r + s for r in "23456789TJQKA" for s in "shdc"]
_DECK = [eval7.Card(c) for c in _FULL]
_IDX = {str(c): k for k, c in enumerate(_DECK)}
# kombinacje klas jako pary indeksow kart
_COMBOS = [[(_IDX[str(c1)], _IDX[str(c2)]) for (c1, c2), _w in eval7.HandRange(cls).hands]
           for cls in CLASSES]
_R52 = range(52)


def _cell(i: int, j: int) -> float:
    ci, cj = _COMBOS[i], _COMBOS[j]
    rng = random.Random(i * N169 + j)
    samp = rng.sample
    ev = eval7.evaluate
    D = _DECK
    s = 0.0; done = 0
    while done < N:
        a1, a2 = rng.choice(ci)
        b1, b2 = rng.choice(cj)
        hole = (a1, a2, b1, b2)
        if len(set(hole)) < 4:            # kolizja kart hole
            continue
        bd = samp(_R52, 5)
        if not set(bd).isdisjoint(hole):  # plansza koliduje z hole -> ponow
            continue
        board = [D[k] for k in bd]
        hv = ev([D[a1], D[a2]] + board); vv = ev([D[b1], D[b2]] + board)
        if hv > vv: s += 1.0
        elif hv == vv: s += 0.5
        done += 1
    return s / N


def load():
    return json.load(open(CACHE)) if os.path.exists(CACHE) else [[-1.0] * N169 for _ in range(N169)]


def save(m):
    json.dump(m, open(CACHE, "w"))


def build(start: int, end: int):
    m = load()
    for i in range(start, min(end, N169)):
        m[i][i] = 0.5
        changed = False
        for j in range(i + 1, N169):
            if m[i][j] < 0:
                e = _cell(i, j); m[i][j] = e; m[j][i] = 1.0 - e; changed = True
        if changed:
            save(m)
    filled = sum(1 for i in range(N169) for j in range(N169) if m[i][j] >= 0)
    print(f"rows [{start},{end}) done. filled {filled}/{N169*N169}")


if __name__ == "__main__":
    build(int(sys.argv[1]), int(sys.argv[2]))
