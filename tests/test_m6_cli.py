"""M6 — walidacja interfejsu spotu (CLI/JSON)."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pushfold.cli import hand_to_class, solve_spot


def test_hand_to_class():
    assert hand_to_class("As Kd") == "AKo"
    assert hand_to_class("Kd As") == "AKo"      # kolejnosc bez znaczenia
    assert hand_to_class("Ah Ad") == "AA"
    assert hand_to_class("Ts 9s") == "T9s"
    assert hand_to_class("7d 2c") == "72o"


def test_hu_routing_and_decision():
    r = solve_spot({"mode": "cev", "spot": "hu", "stack_bb": 10, "hero": "As Kd"})
    assert r["sb_shove_pct"] == 57.8 and r["bb_call_pct"] == 37.3
    assert r["hero_class"] == "AKo" and r["decision"] == "SHOVE"


def test_firstin_routing_and_decision():
    r = solve_spot({"mode": "cev", "spot": "firstin", "position": "UTG",
                    "stack_bb": 10, "hero": "7d 2c"})
    assert r["position"] == "UTG" and r["decision"] == "FOLD"
    r2 = solve_spot({"mode": "cev", "spot": "firstin", "position": "BTN",
                     "stack_bb": 10, "hero": "As Ah"})
    assert r2["decision"] == "SHOVE"


def test_icm_routing_and_threshold():
    r = solve_spot({"mode": "icm", "spot": "hu", "stacks": [10, 10, 10, 10],
                    "payouts": [50, 30, 20, 0], "sb_index": 0, "bb_index": 1, "hero": "9h 9d"})
    assert r["bb_call_pct"] == 11.8 and abs(r["bb_call_threshold_eq"] - 0.609) < 0.01
    assert r["decision"] == "SHOVE"


def test_decision_matches_range_membership():
    r = solve_spot({"mode": "cev", "spot": "hu", "stack_bb": 10, "hero": "Qh 2d"})
    in_range = r["hero_class"] in set(r["sb_shove_range"])
    assert (r["decision"] == "SHOVE") == in_range


def test_output_is_json_serializable():
    r = solve_spot({"mode": "cev", "spot": "hu", "stack_bb": 10})
    json.dumps(r)   # nie rzuca
    assert "raise_sizing" in r and r["raise_sizing"]["small"] is None  # placeholder (sekcja 9)


if __name__ == "__main__":
    for fn in [test_hand_to_class, test_hu_routing_and_decision, test_firstin_routing_and_decision,
               test_icm_routing_and_threshold, test_decision_matches_range_membership,
               test_output_is_json_serializable]:
        fn(); print("ok:", fn.__name__)
    print("M6 all passed")
