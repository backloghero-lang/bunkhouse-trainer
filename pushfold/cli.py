"""M6 — interfejs spotu push/fold (JSON-in / JSON-out + czytelny CLI).

Fundament pod 'Analize rozdania': parser obrazu (Haiku) wypluwa stan gry jako JSON,
ten modul liczy decyzje DETERMINISTYCZNYM silnikiem (LLM nigdy nie liczy decyzji).

Schemat wejscia (dict / JSON):
{
  "mode": "cev" | "icm",
  "spot": "hu" | "firstin",            # hu = SB vs BB; firstin = open-shove z pozycji
  "stack_bb": 10.0,                     # efektywny stack (cev/hu/firstin)
  "blinds": {"sb": 0.5, "bb": 1.0},
  "position": "BTN",                    # firstin: UTG..BTN/SB
  "table": "9max" | "6max",
  "hero": "As Kd",                      # opcjonalnie -> decyzja dla reki
  # ICM:
  "stacks": [10,10,10,0], "payouts": [50,30,20,0], "sb_index": 0, "bb_index": 1
}
"""
from __future__ import annotations
import json, sys, argparse

RANKS = "23456789TJQKA"
_RVAL = {r: i for i, r in enumerate(RANKS)}


def hand_to_class(hero: str) -> str:
    """'As Kd' -> 'AKo'; 'Ah Ad' -> 'AA'; 'Ts 9s' -> 'T9s'."""
    a, b = hero.split()
    r1, s1 = a[0], a[1]
    r2, s2 = b[0], b[1]
    if _RVAL[r1] < _RVAL[r2]:
        r1, s1, r2, s2 = r2, s2, r1, s1   # r1 = wyzsza ranga
    if r1 == r2:
        return r1 + r2
    return r1 + r2 + ("s" if s1 == s2 else "o")


def solve_spot(spec: dict) -> dict:
    mode = spec.get("mode", "cev")
    spot = spec.get("spot", "hu")
    blinds = spec.get("blinds", {"sb": 0.5, "bb": 1.0})
    sb, bb = blinds["sb"], blinds["bb"]
    hero = spec.get("hero")
    out = {"mode": mode, "spot": spot}

    if mode == "icm":
        from pushfold.icm_pushfold import solve_pushfold_icm, range_pct, bb_call_threshold
        stacks = spec["stacks"]; payouts = spec["payouts"]
        si = spec.get("sb_index", 0); bi = spec.get("bb_index", 1)
        shove, call = solve_pushfold_icm(stacks, payouts, si, bi, sb, bb)
        out["sb_shove_pct"] = round(range_pct(shove), 1)
        out["bb_call_pct"] = round(range_pct(call), 1)
        out["bb_call_threshold_eq"] = round(bb_call_threshold(stacks, payouts, si, bi, sb, bb), 3)
        out["sb_shove_range"] = shove
        out["bb_call_range"] = call
        shove_set = set(shove)
        out["grid"] = _grid(shove_set)
        if hero:
            cls = hand_to_class(hero)
            out["hero"], out["hero_class"] = hero, cls
            out["decision"] = "SHOVE" if cls in shove_set else "FOLD"
        return out

    # cEV
    E = float(spec.get("stack_bb", 10.0))
    if spot == "hu":
        from pushfold.hu_nash import solve_hu_nash_cev, range_pct, grid
        shove, call = solve_hu_nash_cev(E, sb, bb)
        out["effective_bb"] = E
        out["sb_shove_pct"] = round(range_pct(shove), 1)
        out["bb_call_pct"] = round(range_pct(call), 1)
        out["sb_shove_range"] = shove
        out["bb_call_range"] = call
        out["grid"] = grid(shove)
        shove_set = set(shove)
    else:  # firstin
        from pushfold.multiway_solver import solve_firstin_cev, range_pct
        from pushfold.positions import behind_blinds, hero_blind, ORDER_9, ORDER_6
        pos = spec.get("position", "BTN")
        order = ORDER_6 if spec.get("table") == "6max" else ORDER_9
        shove, calls = solve_firstin_cev(E, behind_blinds(pos, order),
                                         hero_blind=hero_blind(pos), iters=200, max_callers=2)
        out["position"], out["effective_bb"] = pos, E
        out["open_shove_pct"] = round(range_pct(shove), 1)
        out["open_shove_range"] = shove
        out["grid"] = _grid(set(shove))
        shove_set = set(shove)

    if hero:
        cls = hand_to_class(hero)
        out["hero"], out["hero_class"] = hero, cls
        out["decision"] = "SHOVE" if cls in shove_set else "FOLD"
    # placeholdery sizingu (HANDOFF sekcja 9): tylko shove/fold w preflop push/fold
    out["raise_sizing"] = {"small": None, "mid": None, "big": None,
                           "note": "placeholder; sizing dopiero przy drzewie z raise'ami/postflop"}
    return out


def _grid(selected) -> str:
    sel = set(selected); R = "AKQJT98765432"; rows = []
    for i, hi in enumerate(R):
        line = []
        for j, lo in enumerate(R):
            cls = hi + lo if i == j else (hi + lo + "s" if i < j else lo + hi + "o")
            line.append("X" if cls in sel else ".")
        rows.append(" ".join(line))
    return "\n".join(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Bunkhouse push/fold — silnik decyzji (off-table).")
    ap.add_argument("--file", "-f", help="plik JSON ze spotem")
    ap.add_argument("--json", "-j", help="spot jako string JSON")
    ap.add_argument("--grid", action="store_true", help="pokaz siatke 13x13")
    args = ap.parse_args(argv)
    if args.file:
        spec = json.load(open(args.file))
    elif args.json:
        spec = json.loads(args.json)
    else:
        spec = json.load(sys.stdin)
    res = solve_spot(spec)
    grid = res.pop("grid", None)
    print(json.dumps(res, ensure_ascii=False, indent=2))
    if args.grid and grid:
        print("\nSHOVE grid (X=shove):\n" + grid, file=sys.stderr)
    return res


if __name__ == "__main__":
    main()
