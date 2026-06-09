"""Pozycje pelnego stolu -> lista blindow graczy z tylu dla open-shove first-in.

Tylko SB i BB postuja; pozostali z tylu maja blind 0 (martwe 0). Hero (pierwszy do akcji
w nieotwartym potcie) postuje 0, chyba ze sam jest na SB/BB.
"""
SB, BB = 0.5, 1.0

# 9-max: kolejnosc akcji preflop: UTG,UTG1,MP,LJ,HJ,CO,BTN,SB,BB
ORDER_9 = ["UTG", "UTG1", "MP", "LJ", "HJ", "CO", "BTN", "SB", "BB"]
ORDER_6 = ["UTG", "MP", "CO", "BTN", "SB", "BB"]


def behind_blinds(position, order=ORDER_9):
    """Blindy graczy SIEDZACYCH ZA hero (do BB wlacznie). Hero open-shove first-in."""
    i = order.index(position)
    behind = order[i + 1:]
    return [SB if p == "SB" else BB if p == "BB" else 0.0 for p in behind]


def hero_blind(position):
    return SB if position == "SB" else BB if position == "BB" else 0.0
