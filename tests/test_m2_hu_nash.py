"""M2 — walidacja HU chip-EV Nash push/fold solvera (HANDOFF M2 + sekcja 7)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pushfold.hu_nash import solve_hu_nash_cev, range_pct


def test_convergence_stable():
    """Usrednione fictitious play zbiega: iters=300 == iters=600."""
    a = solve_hu_nash_cev(10.0, iters=300)
    b = solve_hu_nash_cev(10.0, iters=600)
    assert a == b, "solver nie zbiegl (300 != 600 iteracji)"


def test_monotone_tightening_with_depth():
    """Im glebszy stack, tym wezsze range shove (SB) i call (BB)."""
    depths = [3, 5, 8, 10, 12, 15, 20, 25]
    sb = [range_pct(solve_hu_nash_cev(float(E))[0]) for E in depths]
    bb = [range_pct(solve_hu_nash_cev(float(E))[1]) for E in depths]
    assert all(sb[k] >= sb[k+1] - 1e-9 for k in range(len(sb)-1)), f"SB niemonotoniczny: {sb}"
    assert all(bb[k] >= bb[k+1] - 1e-9 for k in range(len(bb)-1)), f"BB niemonotoniczny: {bb}"


def test_short_stack_limit_any_two():
    """Przy ~1bb gra degeneruje sie do any-two (znany limit)."""
    s, c = solve_hu_nash_cev(1.0)
    assert range_pct(s) == 100.0 and range_pct(c) == 100.0


def test_bb_call_threshold_is_analytic():
    """BB calluje DOKLADNIE klasy z equity > (E-bb)/2E vs finalny shove SB."""
    from pushfold.hu_nash import CLASSES, _eq_vs_weighted
    E, bb = 10.0, 1.0
    s, c = solve_hu_nash_cev(E)
    sb_avg = [1.0 if CLASSES[i] in set(s) else 0.0 for i in range(169)]
    thr = (E - bb) / (2 * E)
    cset = set(c)
    for i, cls in enumerate(CLASSES):
        eq = _eq_vs_weighted(i, sb_avg)
        # trzon: poza pasmem +-0.01 wokol progu czlonkostwo musi sie zgadzac;
        # hands graniczne (w pasmie) tolerujemy (sekcja 7 + artefakt usredniania FP)
        if eq > thr + 0.01:
            assert cls in cset, f"{cls} eq={eq:.3f}>>thr ale nie w call"
        elif eq < thr - 0.01:
            assert cls not in cset, f"{cls} eq={eq:.3f}<<thr ale w call"


def test_10bb_trunk_ranges():
    """Trzon range'a 10bb HU Nash (porownanie z publikowanymi: SB ~57-60%, BB ~37-40%)."""
    s, c = solve_hu_nash_cev(10.0)
    ps, pc = range_pct(s), range_pct(c)
    assert 52.0 <= ps <= 63.0, f"SB shove 10bb = {ps:.1f}% poza trzonem"
    assert 32.0 <= pc <= 43.0, f"BB call 10bb = {pc:.1f}% poza trzonem"
    sset, cset = set(s), set(c)
    for must in ["AA", "KK", "AKs", "AKo", "22"]:
        assert must in sset, f"{must} powinno byc w SB shove 10bb"
        assert must in cset, f"{must} powinno byc w BB call 10bb"
    for trash in ["72o", "32o", "82o"]:
        assert trash not in cset, f"{trash} nie powinno callowac 10bb"


if __name__ == "__main__":
    for fn in [test_convergence_stable, test_monotone_tightening_with_depth,
               test_short_stack_limit_any_two, test_bb_call_threshold_is_analytic,
               test_10bb_trunk_ranges]:
        fn(); print("ok:", fn.__name__)
    print("M2 all passed")
