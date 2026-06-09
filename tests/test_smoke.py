"""M0 smoke testy (HANDOFF: PIERWSZE ZADANIE DLA AGENTA, pkt 2)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pushfold.equity import hand_vs_hand_equity
from pushfold.icm import calculate_icm, calculate_icm_crosscheck


def test_equity_AKo_vs_QQ():
    """(a) Znany matchup: AKo vs QQ ~ 43/57 (HANDOFF M1)."""
    eq = hand_vs_hand_equity(["As", "Kd"], ["Qh", "Qc"])
    assert 0.42 <= eq <= 0.44, f"AKo equity poza zakresem: {eq:.4f}"


def test_equity_AKs_vs_22():
    """Drugi znany punkt z M1: AKs vs 22 ~ 50/50 (race)."""
    eq = hand_vs_hand_equity(["As", "Ks"], ["2h", "2c"])
    assert 0.48 <= eq <= 0.52, f"AKs vs 22 equity poza zakresem: {eq:.4f}"


def test_icm_3players():
    """(b) calculate_icm dla [5000,3000,2000] przy wyplatach [50,30,20].
    Recznie policzony Malmuth-Harville (patrz NOTES_theory.md):
      A=38.393, B=32.750, C=28.857; suma == 100."""
    eq = calculate_icm([5000, 3000, 2000], [50, 30, 20])
    expected = [38.3929, 32.7500, 28.8571]
    for got, exp in zip(eq, expected):
        assert abs(got - exp) < 1e-3, f"ICM mismatch: {got} vs {exp}"
    assert abs(sum(eq) - 100.0) < 1e-9, f"suma equity != pula nagrod: {sum(eq)}"


def test_icm_crosscheck_if_pokerkit():
    """Jesli pokerkit jest zainstalowany (Python>=3.11), nasz MH == pokerkit.calculate_icm."""
    mine, ref = calculate_icm_crosscheck([5000, 3000, 2000], [50, 30, 20])
    if ref is None:
        return  # pokerkit niedostepny w tym srodowisku — pomijamy
    for a, b in zip(mine, ref):
        assert abs(a - b) < 1e-6, f"MH != pokerkit: {a} vs {b}"


if __name__ == "__main__":
    test_equity_AKo_vs_QQ()
    test_equity_AKs_vs_22()
    test_icm_3players()
    test_icm_crosscheck_if_pokerkit()
    print("all smoke tests passed")
