"""M7 — first-in pod ICM (pozycyjne, rowne stacki)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pushfold.icm_firstin import solve_firstin_icm, range_pct
from pushfold.multiway_solver import solve_firstin_cev, range_pct as rpc
from pushfold.icm_pushfold import solve_pushfold_icm, range_pct as rp4


def test_wta_reduces_to_cev_exactly():
    """ZLOTY test: winner-take-all (ICM liniowe) == DOKLADNIE cEV (M5c)."""
    hi, _ = solve_firstin_icm(10.0, 3, [1], [0.5, 1.0], hero_blind=0.0, behind_idx=[1, 2], iters=250)
    hc, _ = solve_firstin_cev(10.0, [0.5, 1.0], hero_blind=0.0, iters=250)
    assert set(hi) == set(hc), (range_pct(hi), rpc(hc))


def test_callers_tighten_under_icm():
    """Range'y callerow zacieśniają się pod ICM (flat 3-paid) vs WTA."""
    _, cw = solve_firstin_icm(10.0, 3, [100, 0, 0], [0.5, 1.0], hero_blind=0.0, behind_idx=[1, 2], iters=200)
    _, ci = solve_firstin_icm(10.0, 3, [50, 30, 20], [0.5, 1.0], hero_blind=0.0, behind_idx=[1, 2], iters=200)
    assert range_pct(ci[0]) < range_pct(cw[0])
    assert range_pct(ci[1]) < range_pct(cw[1])


def test_hu_reduces_to_M4_trunk():
    """1 gracz z tylu pod ICM ~ M4 (banka), z tolerancja granicy."""
    _, ci = solve_firstin_icm(10.0, 4, [50, 30, 20, 0], [1.0], hero_blind=0.5, hero_i=0, behind_idx=[1], iters=250)
    _, c4 = solve_pushfold_icm([10, 10, 10, 10], [50, 30, 20, 0], 0, 1, 0.5, 1.0)
    assert abs(range_pct(ci[0]) - rp4(c4)) < 2.0


def test_open_shover_premiums_in():
    h, _ = solve_firstin_icm(10.0, 3, [50, 30, 20], [0.5, 1.0], hero_blind=0.0, behind_idx=[1, 2], iters=200)
    assert all(x in set(h) for x in ["AA", "KK", "AKs"])


if __name__ == "__main__":
    for fn in [test_wta_reduces_to_cev_exactly, test_callers_tighten_under_icm,
               test_hu_reduces_to_M4_trunk, test_open_shover_premiums_in]:
        fn(); print("ok:", fn.__name__)
    print("M7 all passed")
