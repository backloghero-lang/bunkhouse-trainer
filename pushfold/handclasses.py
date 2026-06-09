"""169 kanonicznych klas rak preflop + helpery (reprezentanci, kombinacje, range-string)."""
from __future__ import annotations

RANKS = "23456789TJQKA"
_RIDX = {r: i for i, r in enumerate(RANKS)}


def all_classes() -> list[str]:
    """169 klas: 'AA'..'22' (pary), 'AKs'... (suited), 'AKo'... (offsuit)."""
    out = []
    n = len(RANKS)
    for i in range(n - 1, -1, -1):      # wyzsza ranga
        for j in range(n - 1, -1, -1):  # nizsza ranga
            hi, lo = RANKS[i], RANKS[j]
            if i == j:
                out.append(hi + lo)            # para
            elif i > j:
                out.append(hi + lo + "s")      # suited
            else:
                out.append(lo + hi + "o")      # offsuit (raz)
    # usun duplikaty offsuit/suited z powyzszej petli — generujemy czysto ponizej
    return canonical_169()


def canonical_169() -> list[str]:
    out = []
    n = len(RANKS)
    for i in range(n - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if i == j:
                out.append(RANKS[i] * 2)
            elif i > j:
                out.append(RANKS[i] + RANKS[j] + "s")
            else:
                out.append(RANKS[j] + RANKS[i] + "o")
    # deduplikacja z zachowaniem kolejnosci
    seen, res = set(), []
    for c in out:
        if c not in seen:
            seen.add(c); res.append(c)
    return res


def combos(cls: str) -> int:
    if len(cls) == 2:
        return 6          # para
    return 4 if cls.endswith("s") else 12


def representative(cls: str) -> tuple[str, str]:
    """Jedna reprezentatywna kombinacja klasy (do equity)."""
    if len(cls) == 2:                       # para, np. 'AA'
        r = cls[0]; return (r + "s", r + "h")
    hi, lo = cls[0], cls[1]
    if cls.endswith("s"):
        return (hi + "s", lo + "s")
    return (hi + "s", lo + "h")             # offsuit


def class_set_to_range_string(classes) -> str:
    """Zbior klas -> string range'a eval7 (np. 'AA,KK,AKs,AKo')."""
    return ",".join(classes)


TOTAL_COMBOS = 1326
