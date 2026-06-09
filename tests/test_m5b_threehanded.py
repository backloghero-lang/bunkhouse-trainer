"""M5b — 3-handed first-in push/fold (model niezaleznych callerow)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pushfold.multiway_solver import solve_firstin_cev, range_pct
from pushfold.hu_nash import solve_hu_nash_cev


def test_reduction_one_behind_equals_M2():
    """ZLOTY test: 1 gracz z tylu (HU SB vs BB) == DOKLADNIE solver M2."""
    h, calls = solve_firstin_cev(10.0, [1.0], hero_blind=0.5, iters=300)
    s2, c2 = solve_hu_nash_cev(10.0)
    assert set(h) == set(s2), (range_pct(h), range_pct(s2))
    assert set(calls[0]) == set(c2)


def test_btn_tighter_than_hu():
    """3-handed BTN (dwoch callerow z tylu) wezszy niz HU SB (jeden)."""
    h3, _ = solve_firstin_cev(10.0, [0.5, 1.0], hero_blind=0.0, iters=200)
    s2, _ = solve_hu_nash_cev(10.0)
    assert range_pct(h3) < range_pct(s2)


def test_monotone_with_depth():
    prev = 200.0
    for E in [6, 8, 10, 12, 15, 20]:
        p = range_pct(solve_firstin_cev(float(E), [0.5, 1.0], hero_blind=0.0, iters=200)[0])
        assert p <= prev + 1e-9, (E, p, prev)
        prev = p


def test_structure_premiums_in_trash_out():
    h, _ = solve_firstin_cev(10.0, [0.5, 1.0], hero_blind=0.0, iters=200)
    hs = set(h)
    assert all(x in hs for x in ["AA", "KK", "QQ", "AKs", "AKo"])
    assert all(x not in hs for x in ["72o", "32o", "82o"])


if __name__ == "__main__":
    for fn in [test_reduction_one_behind_equals_M2, test_btn_tighter_than_hu,
               test_monotone_with_depth, test_structure_premiums_in_trash_out]:
        fn(); print("ok:", fn.__name__)
    print("M5b all passed")
