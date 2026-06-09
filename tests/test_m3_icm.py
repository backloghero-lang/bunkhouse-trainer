"""M3 — walidacja ICM engine (HANDOFF M3 + sekcja 7).

Niezalezne wzorce: (a) enumeracja permutacji, (b) zamknieta forma HU,
(c) opublikowany przyklad liczbowy, (d) wlasnosci modelu."""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pushfold.icm import calculate_icm, icm_bruteforce, icm_headsup


def test_published_anchor():
    """Opublikowany przyklad: [5000,2500,2500]/[50,30,20] -> [38.33,30.83,30.83]."""
    eq = calculate_icm([5000, 2500, 2500], [50, 30, 20])
    for got, exp in zip(eq, [38.33, 30.83, 30.83]):
        assert abs(got - exp) < 0.01, f"{got} vs {exp}"


def test_recursive_equals_bruteforce():
    """calculate_icm (rekurencja) == icm_bruteforce (permutacje) na losowych spotach."""
    random.seed(0)
    for _ in range(300):
        n = random.randint(2, 6)
        stacks = [random.randint(50, 9000) for _ in range(n)]
        pays = [50, 30, 20, 10][:random.randint(1, 4)]
        a, b = calculate_icm(stacks, pays), icm_bruteforce(stacks, pays)
        assert max(abs(x - y) for x, y in zip(a, b)) < 1e-9, (stacks, pays)


def test_headsup_closed_form():
    for stacks in ([6000, 4000], [8000, 2000], [5000, 5000]):
        a, b = calculate_icm(stacks, [50, 30]), icm_headsup(stacks, [50, 30])
        assert max(abs(x - y) for x, y in zip(a, b)) < 1e-9


def test_equal_stacks_equal_equity():
    eq = calculate_icm([3000, 3000, 3000, 3000], [50, 30, 20])
    assert all(abs(x - 25.0) < 1e-9 for x in eq)   # pula 100 / 4 graczy


def test_sum_equals_prizepool():
    eq = calculate_icm([4000, 3000, 2000, 1000], [50, 30, 20])
    assert abs(sum(eq) - 100.0) < 1e-9


def test_monotone_more_chips_more_equity():
    eq = calculate_icm([5000, 3000, 2000], [50, 30, 20])
    assert eq[0] > eq[1] > eq[2]


def test_icm_compression():
    """ICM kompresuje: $ na zeton lidera < $ na zeton krotkiego (nieliniowosc)."""
    stacks = [7000, 2000, 1000]
    eq = calculate_icm(stacks, [50, 30, 20])
    per_chip = [e / s for e, s in zip(eq, stacks)]
    assert per_chip[0] < per_chip[2], f"brak kompresji ICM: {per_chip}"


def test_chipleader_below_proportional():
    """Lider z polowa zetonow ma < 50% puli (znana wlasnosc ICM)."""
    stacks = [5000, 2500, 2500]                 # lider 50% zetonow
    eq = calculate_icm(stacks, [50, 30, 20])    # pula 100
    assert eq[0] < 50.0                          # 38.33 < 50


if __name__ == "__main__":
    for fn in [test_published_anchor, test_recursive_equals_bruteforce, test_headsup_closed_form,
               test_equal_stacks_equal_equity, test_sum_equals_prizepool,
               test_monotone_more_chips_more_equity, test_icm_compression,
               test_chipleader_below_proportional]:
        fn(); print("ok:", fn.__name__)
    print("M3 all passed")
