"""Prekompilacja PRAWDZIWYCH zakresow z silnika -> web/ranges.json (do wbudowania w strone).

Model (ujawniony w UI): stol 9-handed, rowne stacki E; etap zmienia tylko strukture wyplat:
  early  = cEV (bez ICM),
  bubble = ICM, twarda banka (top 4 platne, 5. = 0),
  ft     = ICM, struktura finalowego stolu (9 platnych).
Pozycje = miejsca 9-max. Open-shove first-in z pozycji; obrona = BB vs open-shove z BTN.
"""
import json, os, sys
from pushfold.multiway_solver import solve_firstin_cev, range_pct as rpc
from pushfold.icm_firstin import solve_firstin_icm, range_pct as rpi
from pushfold.firstin_mc import hero_open_range
from pushfold.handclasses import combos as _combos
from pushfold.payouts import MTT_FT_9

ORDER = ["UTG", "UTG1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
SEAT = {p: i for i, p in enumerate(ORDER)}
UI_POS = ["UTG", "MP", "CO", "BTN", "SB"]          # pozycje open-shove w UI (BB nie otwiera)
STACKS = [4, 6, 8, 10, 12, 15, 20]
BUBBLE_9 = [40, 28, 19, 13, 0, 0, 0, 0, 0]          # twarda banka 9-max (suma 100)
STAGES = {"early": None, "bubble": BUBBLE_9, "ft": MTT_FT_9}


def _behind(pos):
    i = SEAT[pos]
    idxs = list(range(i + 1, 9))
    blinds = [0.5 if ORDER[j] == "SB" else 1.0 if ORDER[j] == "BB" else 0.0 for j in idxs]
    hb = 0.5 if pos == "SB" else 1.0 if pos == "BB" else 0.0
    return i, idxs, blinds, hb


def _freqs(calls):
    return [sum(_combos(c) for c in cs) / 1326 for cs in calls]


def open_range(stage, E, pos):
    i, idxs, blinds, hb = _behind(pos)
    if not idxs:
        return []
    if len(idxs) <= 2:
        # <=2 z tylu: tani solver jest dokladny (SB=M2, BTN itp.)
        if stage == "early":
            h, _ = solve_firstin_cev(E, blinds, hero_blind=hb, iters=250, max_callers=2)
        else:
            h, _ = solve_firstin_icm(E, 9, STAGES[stage], blinds, hero_blind=hb,
                                     hero_i=i, behind_idx=idxs, iters=200, max_callers=2)
        return h
    # wielu z tylu: range callerow z taniego FP, range hero z MC z partycypacja
    if stage == "early":
        _, calls = solve_firstin_cev(E, blinds, hero_blind=hb, iters=120, max_callers=2)
        return hero_open_range(E, blinds, calls, _freqs(calls), hero_blind=hb, n_mc=1500, seed=11)
    _, calls = solve_firstin_icm(E, 9, STAGES[stage], blinds, hero_blind=hb,
                                 hero_i=i, behind_idx=idxs, iters=100, max_callers=2)
    return hero_open_range(E, blinds, calls, _freqs(calls), n_players=9, payouts=STAGES[stage],
                           hero_i=i, behind_idx=idxs, hero_blind=hb, n_mc=1200, seed=11)


def defend_range(stage, E):
    """BB calluje vs open-shove z BTN (najczestszy spot obrony)."""
    i, idxs, blinds, hb = _behind("BTN")     # BTN open, behind = SB,BB
    if stage == "early":
        _, calls = solve_firstin_cev(E, blinds, hero_blind=hb, iters=150, max_callers=2)
    else:
        _, calls = solve_firstin_icm(E, 9, STAGES[stage], blinds, hero_blind=hb,
                                     hero_i=i, behind_idx=idxs, iters=120, max_callers=2)
    return sorted(calls[-1])   # ostatni behind = BB (set -> list)


def build_one(stage, E):
    webdir = os.path.join(os.path.dirname(__file__), "..", "web")
    os.makedirs(webdir, exist_ok=True)
    entry = {"push": {}, "call": defend_range(stage, float(E))}
    for pos in UI_POS:
        entry["push"][pos] = open_range(stage, float(E), pos)
    out = os.path.join(webdir, f"cell_{stage}_{E}.json")
    json.dump(entry, open(out, "w"))
    print(f"{stage} {E}BB done -> {out}")


def merge():
    webdir = os.path.join(os.path.dirname(__file__), "..", "web")
    data = {}
    for stage in STAGES:
        data[stage] = {}
        for E in STACKS:
            f = os.path.join(webdir, f"cell_{stage}_{E}.json")
            if os.path.exists(f):
                data[stage][str(E)] = json.load(open(f))
    json.dump(data, open(os.path.join(webdir, "ranges.json"), "w"))
    print("merged ->", os.path.join(webdir, "ranges.json"),
          "| stages:", {k: len(v) for k, v in data.items()})


if __name__ == "__main__":
    if sys.argv[1] == "merge":
        merge()
    elif len(sys.argv) == 3:
        build_one(sys.argv[1], int(sys.argv[2]))
    else:
        for E in STACKS:
            build_one(sys.argv[1], E)
