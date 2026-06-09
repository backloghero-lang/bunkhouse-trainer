"""M5c — first-in open-shove vs pelny stol (charty pozycyjne)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pushfold.multiway_solver import solve_firstin_cev, range_pct
from pushfold.positions import behind_blinds, hero_blind, ORDER_9
from pushfold.hu_nash import solve_hu_nash_cev


def _solve_pos(pos, E):
    return solve_firstin_cev(E, behind_blinds(pos), hero_blind=hero_blind(pos),
                             iters=200, max_callers=2)[0]


def test_behind_blinds_helper():
    bb = behind_blinds("UTG", ORDER_9)
    assert len(bb) == 8 and bb[-2:] == [0.5, 1.0] and bb[:-2] == [0.0] * 6
    assert behind_blinds("BTN", ORDER_9) == [0.5, 1.0]
    assert behind_blinds("CO", ORDER_9) == [0.0, 0.5, 1.0]


def test_positional_monotone_tighter_earlier():
    """UTG <= MP <= CO <= BTN <= SB (wczesniejsza pozycja => ciasniej)."""
    pcts = [range_pct(_solve_pos(p, 10.0)) for p in ["UTG", "MP", "CO", "BTN", "SB"]]
    assert all(pcts[k] <= pcts[k+1] + 1e-9 for k in range(len(pcts)-1)), pcts


def test_sb_equals_M2():
    """SB first-in (1 gracz z tylu) == DOKLADNIE solver M2."""
    h = _solve_pos("SB", 10.0)
    s2, _ = solve_hu_nash_cev(10.0)
    assert set(h) == set(s2)


def test_each_position_monotone_with_depth():
    for pos in ["UTG", "CO", "BTN"]:
        prev = 200.0
        for E in [6, 10, 15, 20]:
            p = range_pct(_solve_pos(pos, float(E)))
            assert p <= prev + 1e-9, (pos, E, p, prev)
            prev = p


def test_premiums_shoved_everywhere():
    for pos in ["UTG", "MP", "CO", "BTN"]:
        hs = set(_solve_pos(pos, 10.0))
        assert all(x in hs for x in ["AA", "KK", "AKs"]), pos


if __name__ == "__main__":
    for fn in [test_behind_blinds_helper, test_positional_monotone_tighter_earlier,
               test_sb_equals_M2, test_each_position_monotone_with_depth,
               test_premiums_shoved_everywhere]:
        fn(); print("ok:", fn.__name__)
    print("M5c all passed")
