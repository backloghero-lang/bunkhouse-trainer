"""M1 — walidacja equity engine (HANDOFF M1 + sekcja 7).

Znane matchupy liczone EXACT; cross-check exact vs seeded Monte Carlo < 0.5%."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pushfold.equity import hand_vs_range_equity, range_vs_range_equity


def test_AKo_vs_QQ_range_exact():
    eq = hand_vs_range_equity(["As", "Kd"], "QQ", exact=True)
    assert 0.42 <= eq <= 0.44, f"AKo vs QQ = {eq:.4f}"   # ~43/57


def test_AKs_vs_22_range_exact():
    eq = hand_vs_range_equity(["As", "Ks"], "22", exact=True)
    assert 0.48 <= eq <= 0.52, f"AKs vs 22 = {eq:.4f}"   # ~50/50


def test_AA_vs_KK_exact():
    eq = hand_vs_range_equity(["As", "Ac"], "KK", exact=True)
    assert 0.80 <= eq <= 0.84, f"AA vs KK = {eq:.4f}"    # ~82


def test_exact_vs_seeded_mc_under_half_percent():
    """Sekcja 7: equity vs niezalezna metoda < 0.5%. Tu: exact vs wlasny seeded MC."""
    ex = hand_vs_range_equity(["As", "Ac"], "KK", exact=True)
    mc = hand_vs_range_equity(["As", "Ac"], "KK", exact=False, iterations=60000, seed=1234)
    assert abs(ex - mc) < 0.005, f"|exact-mc| = {abs(ex-mc):.4f}"


def test_mc_deterministic_with_seed():
    """Ten sam seed => identyczny wynik (powtarzalnosc, rule 4)."""
    a = hand_vs_range_equity(["As", "Kd"], "QQ", exact=False, iterations=20000, seed=99)
    b = hand_vs_range_equity(["As", "Kd"], "QQ", exact=False, iterations=20000, seed=99)
    assert a == b, f"MC niedeterministyczny: {a} != {b}"


def test_range_vs_range_runs():
    eq = range_vs_range_equity("AKs", "QQ-TT", exact=False, iterations=15000, seed=7)
    assert 0.43 <= eq <= 0.50, f"AKs vs QQ-TT = {eq:.4f}"


if __name__ == "__main__":
    for fn in [test_AKo_vs_QQ_range_exact, test_AKs_vs_22_range_exact, test_AA_vs_KK_exact,
               test_exact_vs_seeded_mc_under_half_percent, test_mc_deterministic_with_seed,
               test_range_vs_range_runs]:
        fn(); print("ok:", fn.__name__)
    print("M1 all passed")


# --------------------------- M1-hardening: regresja + walidacja --------------------------- #
import pytest
from pushfold.equity import hand_vs_hand_equity


def test_domination_AKo_vs_AQo():
    eq = hand_vs_hand_equity(["As", "Kd"], ["Ah", "Qc"])
    assert 0.72 <= eq <= 0.76, f"AKo vs AQo = {eq:.4f}"   # ~74 (dominacja kickerem)


def test_AQs_vs_KK_exact():
    eq = hand_vs_range_equity(["As", "Qs"], "KK", exact=True)
    assert 0.30 <= eq <= 0.34, f"AQs vs KK = {eq:.4f}"    # ~32


def test_weight_uniform_invariance():
    """Jednolita waga range'a nie zmienia equity: 0.5(QQ) == QQ."""
    a = hand_vs_range_equity(["As", "Kd"], "QQ", exact=True)
    b = hand_vs_range_equity(["As", "Kd"], "0.5(QQ)", exact=True)
    assert abs(a - b) < 1e-9, f"waga zmienila equity: {a} vs {b}"


def test_invalid_card_raises():
    with pytest.raises(ValueError):
        hand_vs_hand_equity(["Xs", "Kd"], ["Qh", "Qc"])


def test_duplicate_card_raises():
    with pytest.raises(ValueError):
        hand_vs_hand_equity(["As", "Kd"], ["As", "Qc"])


def test_empty_villain_range_raises():
    """Jedyna kombinacja villaina konfliktuje z reka hero -> range pusty -> ValueError."""
    with pytest.raises(ValueError):
        hand_vs_range_equity(["Ah", "Ad"], "AhAd", exact=True)
