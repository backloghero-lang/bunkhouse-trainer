# Hand Analyzer — ustalona architektura (do zbudowania później)

Tab "Hand Analyzer" (#analyzer). Flow: upload screenshota SKOŃCZONEJ ręki → odtworzenie spotu → werdykt GTO. Off-table, nigdy na żywo / RTA.

Podział odpowiedzialności (twarde założenie: LLM NIGDY nie zgaduje liczb pokerowych):
- AGENT (wizja + język): (1) wyciąga spot ze screenshota — pozycja, efektywny stack w BB, etap, akcja, karty; (2) pisze ludzkie wyjaśnienie werdyktu.
- SILNIK DETERMINISTYCZNY: liczy całość — Nash/ICM, EV push/fold, zakres — i wydaje werdykt. Agent nie dotyka matematyki.

UX: agent proponuje odczytany spot → user potwierdza/poprawia ("ok / popraw") → dopiero wtedy werdykt z silnika (gwarancja poprawnych danych wejściowych).
Parser screenshotów stroić pod konkretny room/layout (GG, PokerStars, ...). Najpierw upload + ręczne potwierdzenie.

Kolejność budowy: 1) Legendary Hands (ZROBIONE), 2) Hand Analyzer.
