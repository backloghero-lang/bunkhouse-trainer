"""M4 — push/fold pod ICM (HANDOFF M4 + sekcja 7)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pushfold.icm_pushfold import solve_pushfold_icm, range_pct, bb_call_threshold
from pushfold.hu_nash import solve_hu_nash_cev, range_pct as rp_cev


def test_winner_take_all_reproduces_cev():
    """ICM liniowe przy winner-take-all => DOKLADNIE zakresy cEV z M2 (zloty test)."""
    si, ci = solve_pushfold_icm([10, 10], [1], 0, 1)
    sc, cc = solve_hu_nash_cev(10.0)
    assert set(si) == set(sc) and set(ci) == set(cc)


def test_caller_tightens_on_bubble():
    """BB calluje wezej na twardej bance niz w cEV; range bankowy ⊆ cEV."""
    stacks = [10, 10, 10, 10]
    _, c_cev = solve_pushfold_icm(stacks, [1], 0, 1)          # WTA = cEV
    _, c_bub = solve_pushfold_icm(stacks, [50, 30, 20, 0], 0, 1)
    assert range_pct(c_bub) < range_pct(c_cev)
    assert set(c_bub).issubset(set(c_cev))


def test_risk_premium_emerges():
    """Risk premium nie jest wpisany: prog calla BB rosnie z 0.45 (cEV) na bance."""
    stacks = [10, 10, 10, 10]
    thr_cev = bb_call_threshold(stacks, [1], 0, 1)            # ~0.45
    thr_bub = bb_call_threshold(stacks, [50, 30, 20, 0], 0, 1)
    assert abs(thr_cev - 0.45) < 0.01
    assert thr_bub > thr_cev + 0.10                          # wyrazna premia za ryzyko


def test_monotone_with_bubble_severity():
    """Im wyzsza nagroda za 4. miejsce (miekka banka), tym szerszy call BB."""
    stacks = [10, 10, 10, 10]
    pcts = []
    for p4 in [0, 5, 10, 15, 20]:
        pay = [(100 - p4) * 0.5, (100 - p4) * 0.3, (100 - p4) * 0.2, p4]
        pcts.append(range_pct(solve_pushfold_icm(stacks, pay, 0, 1)[1]))
    assert all(pcts[k] <= pcts[k+1] + 1e-9 for k in range(len(pcts)-1)), pcts


def test_busted_player_gets_last_place():
    """Spojnosc z ICM: na bance bust=0, ale gdy 4. platne -> bust bierze te nagrode."""
    from pushfold.icm import calculate_icm
    eq = calculate_icm([20, 10, 10, 0], [45, 27, 18, 10])
    assert abs(eq[3] - 10.0) < 1e-9 and abs(sum(eq) - 100.0) < 1e-9


if __name__ == "__main__":
    for fn in [test_winner_take_all_reproduces_cev, test_caller_tightens_on_bubble,
               test_risk_premium_emerges, test_monotone_with_bubble_severity,
               test_busted_player_gets_last_place]:
        fn(); print("ok:", fn.__name__)
    print("M4 all passed")
