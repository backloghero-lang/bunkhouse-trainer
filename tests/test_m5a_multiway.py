"""M5a — walidacja equity multiway (N-way all-in)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pushfold.multiway_equity import multiway_equity


def test_sums_to_one():
    for specs, seed in [(["As Ah", "Ks Kh", "Qs Qh"], 1),
                        (["AhKh", "QsQc", "7d2c", "TsTd"], 2)]:
        e = multiway_equity(specs, iterations=8000, seed=seed)
        assert abs(sum(e) - 1.0) < 1e-9


def test_symmetry_three_equal():
    e = multiway_equity(["AhKh", "AsKs", "AdKd"], iterations=15000, seed=1)
    assert all(abs(x - 1/3) < 0.02 for x in e)


def test_AA_KK_QQ_threeway():
    e = multiway_equity(["As Ah", "Ks Kh", "Qs Qh"], iterations=25000, seed=2)
    assert 0.63 <= e[0] <= 0.71, e          # AA ~0.66-0.68
    assert e[0] > e[1] > e[2]               # AA > KK > QQ


def test_twoway_matches_known():
    e = multiway_equity(["As Kd", "Qh Qc"], iterations=40000, seed=3)
    assert abs(e[0] - 0.428) < 0.01         # AKo vs QQ exact 0.428


def test_deterministic_seed():
    a = multiway_equity(["As Ah", "Ks Kh", "Qs Qh"], iterations=5000, seed=7)
    b = multiway_equity(["As Ah", "Ks Kh", "Qs Qh"], iterations=5000, seed=7)
    assert a == b


if __name__ == "__main__":
    for fn in [test_sums_to_one, test_symmetry_three_equal, test_AA_KK_QQ_threeway,
               test_twoway_matches_known, test_deterministic_seed]:
        fn(); print("ok:", fn.__name__)
    print("M5a all passed")
