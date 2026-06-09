"""ICM engine — Malmuth-Harville (Independent Chip Model), szybka wersja DP O(2^n).

Wlasna implementacja (HANDOFF sekcja 4 dopuszcza); pokerkit.calculate_icm liczy ten
sam model -> cross-check na Py>=3.11.

DP: prob_top[T] = prawdop. ze zbior T zajal TOP |T| miejsc (w dowolnej kolejnosci).
  prob_top[{}] = 1
  prob_top[T]  = sum_{i in T} prob_top[T\{i}] * s_i / (total - sum(T) + s_i)
P(i na miejscu p=|T|+1) = sum_{T: i not in T} prob_top[T] * s_i/(total - sum(T))
equity_i = sum_p P(i,p) * payout[p].  Koszt O(2^n * n) -> 9 graczy natychmiast.

Gracze z 0 zetonow (bust) obslugiwani osobno: koncza na dnie i biora nagrody dolnych
miejsc (s_i/Suma = 0 daloby im 0 wszedzie).
"""
from __future__ import annotations
from typing import Sequence


def calculate_icm(stacks: Sequence[float], payouts: Sequence[float]) -> list[float]:
    """$equity kazdego gracza wg Malmuth-Harville (DP O(2^n)). Suma == suma payouts."""
    n = len(stacks)
    if any(s < 0 for s in stacks):
        raise ValueError("stacki nie moga byc ujemne")
    prizes = (list(payouts) + [0.0] * n)[:n]
    equities = [0.0] * n

    pos_idx = [i for i in range(n) if stacks[i] > 0]
    zero_idx = [i for i in range(n) if stacks[i] == 0]
    m = len(pos_idx)
    if zero_idx:
        bottom = prizes[m:n]
        share = sum(bottom) / len(zero_idx)
        for i in zero_idx:
            equities[i] = share
    if m == 0:
        return equities

    s = [stacks[i] for i in pos_idx]          # stacki dodatnie
    pr = prizes[:m]                            # gorne m nagrod
    total = sum(s)

    # sum(T) dla kazdej maski
    masksum = [0.0] * (1 << m)
    for mask in range(1, 1 << m):
        low = mask & (-mask)
        idx = low.bit_length() - 1
        masksum[mask] = masksum[mask ^ low] + s[idx]

    prob_top = [0.0] * (1 << m)
    prob_top[0] = 1.0
    # equity wg miejsc: dla kazdej maski T (top |T|), kolejny finisher dostaje miejsce |T|+1
    eq_pos = [0.0] * m
    for mask in range(1 << m):
        pt = prob_top[mask]
        if pt == 0.0:
            continue
        place = bin(mask).count("1")          # nastepny finisher bedzie na miejscu place+1 (0-idx place)
        rem_total = total - masksum[mask]
        prize = pr[place] if place < m else 0.0
        # rozdaj: kazdy i poza T wygrywa nastepne miejsce z p = s_i/rem_total
        j = (~mask) & ((1 << m) - 1)
        while j:
            low = j & (-j)
            i = low.bit_length() - 1
            p_i = pt * s[i] / rem_total
            if prize:
                eq_pos[i] += p_i * prize
            prob_top[mask | low] += p_i
            j ^= low

    for k, i in enumerate(pos_idx):
        equities[i] += eq_pos[k]
    return equities


def icm_recursive(stacks, payouts):
    """Wolny wzorzec O(n!) (enumeracja permutacji) — do walidacji DP. Tylko male n."""
    from itertools import permutations
    n = len(stacks)
    prizes = (list(payouts) + [0.0] * n)[:n]
    eq = [0.0] * n
    for order in permutations(range(n)):
        p = 1.0
        rem = sum(stacks)
        for pl in order:
            if rem <= 0:
                p = 0.0
                break
            p *= stacks[pl] / rem
            rem -= stacks[pl]
        for pos, pl in enumerate(order):
            eq[pl] += p * prizes[pos]
    return eq


# alias zgodnosci wstecznej (testy M3 uzywaly icm_bruteforce)
icm_bruteforce = icm_recursive


def icm_headsup(stacks, payouts):
    """Zamknieta forma ICM dla 2 graczy: eq_i = b + (s_i/Suma)*(a-b)."""
    a = payouts[0]
    b = payouts[1] if len(payouts) > 1 else 0.0
    s1, s2 = stacks
    tot = s1 + s2
    return [b + (s1 / tot) * (a - b), b + (s2 / tot) * (a - b)]


def calculate_icm_crosscheck(stacks, payouts):
    mine = calculate_icm(stacks, payouts)
    try:
        from pokerkit.analysis import calculate_icm as pk_icm  # noqa
        return mine, list(pk_icm(tuple(stacks), tuple(payouts)))
    except Exception:
        return mine, None


if __name__ == "__main__":
    print("anchor:", [round(x, 2) for x in calculate_icm([5000, 2500, 2500], [50, 30, 20])])
