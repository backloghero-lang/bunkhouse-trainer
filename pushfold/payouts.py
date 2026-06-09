"""Presety struktur wyplat (procent puli nagrod). calculate_icm przyjmuje dowolna liste.

Uwaga: dokladne % FT w prawdziwych MTT roznia sie miedzy operatorami (potwierdzone
researchem) — ponizsze to typowe, udokumentowane punkty odniesienia; do realnego
turnieju podstaw wlasna strukture.
"""

# 1) Single-table SNG 9-max — uniwersalny standard
SNG_9MAX = [50, 30, 20]

# 2) Single-table SNG 6-max / turbo — standard 65/35
SNG_6MAX = [65, 35]

# 3) Spot bankowy: 4 graczy, 3 platne (4. = 0) — tu ICM najmocniej zacieśnia
BUBBLE_4P_3PAID = [50, 30, 20, 0]

# 4) Przykladowa, plaska struktura finalowego stolu 9-handed MTT (% puli, ilustracyjna)
#    Suma 100. Plaska = wieksze min-cashe, mniejsza premia za 1. miejsce.
MTT_FT_9 = [27, 19, 14, 11, 9, 7, 5.5, 4.3, 3.2]

PRESETS = {
    "SNG_9MAX": SNG_9MAX,
    "SNG_6MAX": SNG_6MAX,
    "BUBBLE_4P_3PAID": BUBBLE_4P_3PAID,
    "MTT_FT_9": MTT_FT_9,
}
