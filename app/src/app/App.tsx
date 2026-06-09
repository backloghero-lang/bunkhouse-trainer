import { useState, useMemo } from "react";
import { RANGES } from "./ranges";
import { Card } from "./components/ui/card";
import { Slider } from "./components/ui/slider";
import { Tabs, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Upload } from "lucide-react";
import { Button } from "./components/ui/button";

type Mode = "open" | "defend";
type Position = "UTG" | "MP" | "CO" | "BTN" | "SB" | "BB";
type Stage = "early" | "bubble" | "final";
type Action = "shove" | "call" | "fold";

const RANKS = ["A", "K", "Q", "J", "T", "9", "8", "7", "6", "5", "4", "3", "2"];

// ── Prawdziwe zakresy z silnika (Nash + ICM), prekompilowane do ranges.ts ──
const STACKS = [4, 6, 8, 10, 12, 15, 20];
const snapStack = (v: number) => STACKS.reduce((a, b) => (Math.abs(b - v) < Math.abs(a - v) ? b : a), STACKS[0]);
const stageKey = (s: Stage) => (s === "final" ? "ft" : s);
const combosOf = (lbl: string) => (lbl.length === 2 ? 6 : lbl.endsWith("s") ? 4 : 12);

function rangeListFor(mode: Mode, position: Position, stage: Stage, stack: number): string[] {
  const E = snapStack(stack);
  const node = RANGES[stageKey(stage)]?.[String(E)];
  if (!node) return [];
  return mode === "open" ? (node.push?.[position] ?? []) : (node.call ?? []);
}

const CHIP_COLORS = [
  "radial-gradient(ellipse at 40% 30%, #e74c4c 0%, #c0392b 55%, #7b241c 100%)",
  "radial-gradient(ellipse at 40% 30%, #f3dd97 0%, #d8b65a 55%, #9a6e20 100%)",
  "radial-gradient(ellipse at 40% 30%, #3498db 0%, #2471a3 55%, #1a4f72 100%)",
  "radial-gradient(ellipse at 40% 30%, #9b59b6 0%, #7d3c98 55%, #512e6b 100%)",
  "radial-gradient(ellipse at 40% 30%, #1abc9c 0%, #148f77 55%, #0e6251 100%)",
];

export default function App() {
  const [mode, setMode] = useState<Mode>("open");
  const [stackDepth, setStackDepth] = useState([8]);
  const [position, setPosition] = useState<Position>("BTN");
  const [stage, setStage] = useState<Stage>("final");
  const [uploadedImage, setUploadedImage] = useState<string | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);

  const rangeSet = useMemo(
    () => new Set(rangeListFor(mode, position, stage, stackDepth[0])),
    [mode, position, stage, stackDepth]
  );
  const widthPct = useMemo(() => {
    let w = 0;
    rangeSet.forEach((l) => (w += combosOf(l)));
    return (100 * w) / 1326;
  }, [rangeSet]);

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (ev) => setUploadedImage(ev.target?.result as string);
      reader.readAsDataURL(file);
    }
  };

  const handleStackChange = (value: number[]) => {
    setStackDepth(value);
    setIsCalculating(true);
    setTimeout(() => setIsCalculating(false), 600);
  };

  const getHandLabel = (row: number, col: number): string => {
    if (row === col) return RANKS[row] + RANKS[col];
    if (row < col) return RANKS[row] + RANKS[col] + "s";
    return RANKS[col] + RANKS[row] + "o";
  };

  const cellAction = (row: number, col: number): Action => {
    if (!rangeSet.has(getHandLabel(row, col))) return "fold";
    return mode === "open" ? "shove" : "call";
  };

  const getActionColor = (action: Action): string => {
    switch (action) {
      case "shove": return "bg-[#74c244]/20 border-[#74c244]/50 hover:bg-[#74c244]/35";
      case "call":  return "bg-[#d99a3a]/20 border-[#d99a3a]/50 hover:bg-[#d99a3a]/35";
      case "fold":  return "bg-[#0d1e2c]/60 border-[#1e3448]/60 hover:bg-[#0d1e2c]/80";
    }
  };

  return (
    <div className="min-h-screen dark relative overflow-x-hidden" style={{ background: "#03070f" }}>

      {/* ═══════════════════════════════════════════
          LAYER 1 — ARENA CEILING & DARK SKY
      ═══════════════════════════════════════════ */}
      <div className="absolute inset-0 pointer-events-none">
        {/* Deep arena dark */}
        <div className="absolute inset-0" style={{
          background: "linear-gradient(180deg, #010409 0%, #03070f 30%, #050d18 60%, #071520 100%)"
        }} />

        {/* WSOP blue arena wash — like the overhead rigs */}
        <div className="absolute inset-x-0 top-0" style={{
          height: "55%",
          background: "radial-gradient(ellipse 120% 80% at 50% -10%, rgba(30,80,160,0.28) 0%, rgba(10,30,80,0.12) 50%, transparent 100%)"
        }} />

        {/* Left rig beam */}
        <div className="absolute" style={{
          top: 0, left: "10%",
          width: "35%", height: "70%",
          background: "linear-gradient(160deg, rgba(50,100,200,0.12) 0%, transparent 60%)",
          transform: "skewX(-10deg)",
        }} />
        {/* Right rig beam */}
        <div className="absolute" style={{
          top: 0, right: "10%",
          width: "35%", height: "70%",
          background: "linear-gradient(200deg, rgba(50,100,200,0.12) 0%, transparent 60%)",
          transform: "skewX(10deg)",
        }} />

        {/* Amber center spotlight — hits the table */}
        <div className="absolute" style={{
          top: "-5%", left: "50%", transform: "translateX(-50%)",
          width: "50%", height: "90%",
          background: "radial-gradient(ellipse 60% 100% at 50% 0%, rgba(216,182,90,0.12) 0%, rgba(216,182,90,0.04) 40%, transparent 70%)",
        }} />

        {/* Ceiling light bar rows — decorative LED strips */}
        {[12, 22, 32].map((top, i) => (
          <div key={`bar${i}`} className="absolute inset-x-0" style={{
            top: `${top}%`, height: 1,
            background: `linear-gradient(90deg, transparent 5%, rgba(80,140,255,${0.06 + i * 0.02}) 20%, rgba(150,180,255,${0.1 + i * 0.02}) 50%, rgba(80,140,255,${0.06 + i * 0.02}) 80%, transparent 95%)`,
          }} />
        ))}

        {/* Suit watermarks — faint decorative ♠ ♥ ♦ ♣ */}
        {["♠", "♥", "♦", "♣"].map((suit, i) => (
          <div key={`suit${i}`} className="absolute select-none" style={{
            top: `${10 + i * 18}%`,
            left: i % 2 === 0 ? "3%" : "94%",
            fontSize: "6rem",
            opacity: 0.025,
            color: i === 1 || i === 2 ? "#c0392b" : "#ece7d2",
            transform: `rotate(${i % 2 === 0 ? -15 : 15}deg)`,
            fontFamily: "Georgia, serif",
          }}>{suit}</div>
        ))}
      </div>

      {/* ═══════════════════════════════════════════
          LAYER 2 — POKER TABLE (visible at bottom)
      ═══════════════════════════════════════════ */}
      <div className="absolute inset-x-0 pointer-events-none" style={{ bottom: "-8%", zIndex: 1 }}>

        {/* Table glow — green uplight */}
        <div className="absolute" style={{
          bottom: "18%", left: "50%", transform: "translateX(-50%)",
          width: "90%", height: "300px",
          background: "radial-gradient(ellipse at 50% 100%, rgba(26,97,73,0.35) 0%, rgba(12,53,39,0.2) 40%, transparent 70%)",
          filter: "blur(20px)",
        }} />

        {/* Outer shadow ring */}
        <div className="absolute" style={{
          bottom: "-6%", left: "50%", transform: "translateX(-50%)",
          width: "96%", height: "72%",
          borderRadius: "50%",
          background: "rgba(0,0,0,0.7)",
          filter: "blur(30px)",
        }} />

        {/* Gold rail */}
        <div className="absolute" style={{
          bottom: "-5%", left: "50%", transform: "translateX(-50%)",
          width: "94%", height: "70%",
          borderRadius: "50%",
          background: "linear-gradient(180deg, #c9a84c 0%, #f3dd97 20%, #a07830 50%, #d8b65a 75%, #8a6520 100%)",
          boxShadow: "0 0 60px rgba(216,182,90,0.4), 0 0 120px rgba(216,182,90,0.15), inset 0 0 40px rgba(0,0,0,0.5)",
        }} />

        {/* Felt surface */}
        <div className="absolute" style={{
          bottom: "-3%", left: "50%", transform: "translateX(-50%)",
          width: "90%", height: "66%",
          borderRadius: "50%",
          background: "radial-gradient(ellipse at 50% 55%, #1e7a58 0%, #165e43 30%, #0f4530 60%, #08291c 100%)",
          boxShadow: "inset 0 -30px 80px rgba(0,0,0,0.6), inset 0 30px 60px rgba(0,0,0,0.3)",
        }} />

        {/* Felt texture subtle lines */}
        <div className="absolute" style={{
          bottom: "-3%", left: "50%", transform: "translateX(-50%)",
          width: "90%", height: "66%",
          borderRadius: "50%",
          backgroundImage: "repeating-linear-gradient(0deg, transparent, transparent 4px, rgba(255,255,255,0.015) 4px, rgba(255,255,255,0.015) 5px), repeating-linear-gradient(90deg, transparent, transparent 4px, rgba(255,255,255,0.01) 4px, rgba(255,255,255,0.01) 5px)",
          overflow: "hidden",
        }} />

        {/* Community cards */}
        {["A♠","K♥","Q♦","J♣","T♠"].map((label, i) => {
          const suit = label.slice(-1);
          const isRed = suit === "♥" || suit === "♦";
          return (
            <div key={`card${i}`} className="absolute" style={{
              bottom: "28%",
              left: `calc(50% + ${(i - 2) * 54 - 8}px)`,
              width: 44, height: 62,
              background: "linear-gradient(150deg, #f5f2e8 0%, #e8e2cc 100%)",
              borderRadius: 5,
              border: "1px solid rgba(210,195,150,0.6)",
              boxShadow: "0 6px 20px rgba(0,0,0,0.7), 0 1px 4px rgba(0,0,0,0.5), inset 0 1px 2px rgba(255,255,255,0.3)",
              display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
              fontSize: 15, fontWeight: 800,
              color: isRed ? "#b5150a" : "#0d0d1a",
              transform: `rotate(${(i - 2) * 1.5}deg)`,
              zIndex: 3,
              fontFamily: "Georgia, serif",
            }}>
              <span style={{ lineHeight: 1 }}>{label[0]}</span>
              <span style={{ fontSize: 12, lineHeight: 1 }}>{suit}</span>
            </div>
          );
        })}

        {/* Dealer button */}
        <div className="absolute" style={{
          bottom: "33%", left: "53.5%",
          width: 30, height: 30, borderRadius: "50%",
          background: "radial-gradient(circle at 35% 35%, #fff 0%, #ddd 40%, #999 100%)",
          border: "2px solid #777",
          boxShadow: "0 3px 10px rgba(0,0,0,0.6)",
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 10, fontWeight: 800, color: "#222",
          zIndex: 3,
        }}>D</div>

        {/* Chips — left stack */}
        {[0,1,2,3,4,5].map(i => (
          <div key={`cL${i}`} className="absolute" style={{
            bottom: `${36 + i * 3.2}%`, left: "26%",
            width: 40, height: 11, borderRadius: "50%",
            background: CHIP_COLORS[i % CHIP_COLORS.length],
            border: "2px solid rgba(255,255,255,0.2)",
            boxShadow: "0 3px 8px rgba(0,0,0,0.5)",
            transform: `translateX(${i * 1}px) rotate(${i * 3}deg)`,
            zIndex: 3,
          }} />
        ))}
        {/* Chips — right stack */}
        {[0,1,2,3].map(i => (
          <div key={`cR${i}`} className="absolute" style={{
            bottom: `${38 + i * 3.5}%`, right: "25%",
            width: 40, height: 11, borderRadius: "50%",
            background: CHIP_COLORS[(i + 2) % CHIP_COLORS.length],
            border: "2px solid rgba(255,255,255,0.2)",
            boxShadow: "0 3px 8px rgba(0,0,0,0.5)",
            zIndex: 3,
          }} />
        ))}
        {/* Pot chips */}
        {[0,1,2,3,4].map(i => (
          <div key={`cP${i}`} className="absolute" style={{
            bottom: `${31 + (i > 2 ? i - 3 : i) * 3.5}%`,
            left: `${49 + (i > 2 ? 3 : -2)}%`,
            width: 36, height: 10, borderRadius: "50%",
            background: CHIP_COLORS[(i + 1) % CHIP_COLORS.length],
            border: "2px solid rgba(255,255,255,0.2)",
            boxShadow: "0 2px 6px rgba(0,0,0,0.5)",
            transform: `rotate(${i * 12}deg)`,
            zIndex: 3,
          }} />
        ))}

        {/* Player seat indicators — subtle arcs */}
        {[
          { bottom: "62%", left: "50%", label: "BTN" },
          { bottom: "55%", left: "22%", label: "SB" },
          { bottom: "55%", left: "72%", label: "BB" },
          { bottom: "30%", left: "15%", label: "UTG" },
          { bottom: "18%", left: "35%", label: "MP" },
          { bottom: "18%", left: "58%", label: "CO" },
        ].map((seat) => (
          <div key={seat.label} className="absolute" style={{
            bottom: seat.bottom, left: seat.label === "BTN" ? `calc(${seat.left} - 16px)` : seat.left,
            zIndex: 4,
          }}>
            <div style={{
              padding: "2px 6px",
              borderRadius: 4,
              background: seat.label === position ? "rgba(216,182,90,0.25)" : "rgba(0,0,0,0.4)",
              border: seat.label === position ? "1px solid rgba(216,182,90,0.6)" : "1px solid rgba(255,255,255,0.08)",
              fontSize: 9, fontWeight: 700,
              color: seat.label === position ? "#f3dd97" : "rgba(255,255,255,0.35)",
              letterSpacing: "0.08em",
            }}>{seat.label}</div>
          </div>
        ))}
      </div>

      {/* ═══════════════════════════════════════════
          LAYER 3 — UI CONTENT
      ═══════════════════════════════════════════ */}
      <div className="relative flex flex-col" style={{ zIndex: 10, minHeight: "100vh" }}>

        {/* ── HEADER ── */}
        <header className="pt-6 pb-4 text-center relative">
          {/* WSOP-style top bar */}
          <div className="absolute inset-x-0 top-0 h-1" style={{
            background: "linear-gradient(90deg, transparent 0%, #d8b65a 20%, #f3dd97 50%, #d8b65a 80%, transparent 100%)"
          }} />

          {/* Crown/bracelet icon */}
          <div className="flex justify-center mb-2">
            <div className="flex items-center gap-2 px-4 py-1 rounded-full" style={{
              background: "rgba(216,182,90,0.08)",
              border: "1px solid rgba(216,182,90,0.2)",
            }}>
              <span style={{ color: "#d8b65a", fontSize: "0.75rem", letterSpacing: "0.3em" }}>♠ ♥ WSOP FINAL TABLE ♦ ♣</span>
            </div>
          </div>

          <h1 style={{
            fontSize: "clamp(2rem, 5vw, 3.5rem)",
            fontWeight: 800,
            letterSpacing: "0.2em",
            textTransform: "uppercase",
            background: "linear-gradient(180deg, #f3dd97 0%, #d8b65a 50%, #a07830 100%)",
            WebkitBackgroundClip: "text",
            WebkitTextFillColor: "transparent",
            backgroundClip: "text",
            textShadow: "none",
            lineHeight: 1,
            fontFamily: "'Georgia', serif",
          }}>BUNKHOUSE</h1>

          <div className="flex items-center justify-center gap-4 mt-2">
            <div style={{ width: 60, height: 1, background: "linear-gradient(90deg, transparent, #d8b65a)" }} />
            <span style={{ color: "#7d8ca6", fontSize: "0.7rem", letterSpacing: "0.25em", textTransform: "uppercase" }}>
              Final Table Trainer · Nash + ICM
            </span>
            <div style={{ width: 60, height: 1, background: "linear-gradient(90deg, #d8b65a, transparent)" }} />
          </div>
        </header>

        {/* ── PANELS ── */}
        <div className="flex-1 px-4 pb-4">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 max-w-[1600px] mx-auto">

            {/* LEFT — Control */}
            <div className="lg:col-span-3">
              <Card style={{
                background: "rgba(7,16,31,0.88)",
                backdropFilter: "blur(20px)",
                border: "1px solid rgba(216,182,90,0.18)",
                boxShadow: "0 8px 40px rgba(0,0,0,0.6), 0 0 0 1px rgba(216,182,90,0.06)",
              }} className="p-5">
                <div className="space-y-5">

                  {/* Panel title */}
                  <div className="flex items-center gap-2 pb-3" style={{ borderBottom: "1px solid rgba(216,182,90,0.1)" }}>
                    <div style={{ width: 3, height: 14, borderRadius: 2, background: "#d8b65a" }} />
                    <span style={{ color: "#ece7d2", fontSize: "0.7rem", letterSpacing: "0.15em", textTransform: "uppercase" }}>Parametry</span>
                  </div>

                  {/* Mode */}
                  <div>
                    <label style={{ display: "block", color: "#7d8ca6", fontSize: "0.65rem", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 8 }}>Tryb</label>
                    <Tabs value={mode} onValueChange={(v) => setMode(v as Mode)} className="w-full">
                      <TabsList className="grid w-full grid-cols-2" style={{ background: "rgba(3,7,15,0.6)", border: "1px solid rgba(216,182,90,0.1)" }}>
                        <TabsTrigger value="open" className="data-[state=active]:bg-[#1a6149] data-[state=active]:text-[#ece7d2] text-[#7d8ca6]">
                          Otwierasz
                        </TabsTrigger>
                        <TabsTrigger value="defend" className="data-[state=active]:bg-[#1a6149] data-[state=active]:text-[#ece7d2] text-[#7d8ca6]">
                          Bronisz
                        </TabsTrigger>
                      </TabsList>
                    </Tabs>
                  </div>

                  {/* Stack */}
                  <div>
                    <div className="flex justify-between items-end mb-2">
                      <label style={{ color: "#7d8ca6", fontSize: "0.65rem", letterSpacing: "0.1em", textTransform: "uppercase" }}>Stack</label>
                      <span style={{ color: "#f3dd97", fontSize: "1.75rem", fontWeight: 700, lineHeight: 1 }}>
                        {stackDepth[0].toFixed(1)}
                        <span style={{ color: "#7d8ca6", fontSize: "0.8rem", marginLeft: 4 }}>BB</span>
                      </span>
                    </div>
                    <Slider
                      value={stackDepth}
                      onValueChange={handleStackChange}
                      min={3} max={25} step={0.5}
                      className="[&_[role=slider]]:bg-[#d8b65a] [&_[role=slider]]:border-[#f3dd97] [&_.bg-primary]:bg-[#d8b65a]"
                    />
                    <div className="flex justify-between mt-1" style={{ color: "#7d8ca6", fontSize: "0.6rem" }}>
                      <span>3 BB</span><span>25 BB</span>
                    </div>
                  </div>

                  {/* Position */}
                  <div>
                    <label style={{ display: "block", color: "#7d8ca6", fontSize: "0.65rem", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 8 }}>Pozycja</label>
                    <div className="grid grid-cols-3 gap-1.5">
                      {(["UTG","MP","CO","BTN","SB","BB"] as Position[]).map(pos => (
                        <button key={pos} onClick={() => setPosition(pos)} style={{
                          padding: "6px 4px", borderRadius: 6, fontSize: "0.8rem", fontWeight: 600,
                          border: `1px solid ${position === pos ? "rgba(216,182,90,0.5)" : "rgba(216,182,90,0.08)"}`,
                          background: position === pos ? "rgba(26,97,73,0.6)" : "rgba(3,7,15,0.5)",
                          color: position === pos ? "#f3dd97" : "#7d8ca6",
                          boxShadow: position === pos ? "0 0 12px rgba(26,97,73,0.3)" : "none",
                          transition: "all 0.15s",
                        }}>{pos}</button>
                      ))}
                    </div>
                  </div>

                  {/* Stage */}
                  <div>
                    <label style={{ display: "block", color: "#7d8ca6", fontSize: "0.65rem", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 8 }}>Etap</label>
                    <div className="flex gap-1.5">
                      {(["early","bubble","final"] as Stage[]).map(stg => (
                        <button key={stg} onClick={() => setStage(stg)} style={{
                          flex: 1, padding: "6px 4px", borderRadius: 6, fontSize: "0.7rem", fontWeight: 600,
                          border: `1px solid ${stage === stg ? "rgba(216,182,90,0.5)" : "rgba(216,182,90,0.08)"}`,
                          background: stage === stg ? "rgba(26,97,73,0.6)" : "rgba(3,7,15,0.5)",
                          color: stage === stg ? "#f3dd97" : "#7d8ca6",
                          transition: "all 0.15s",
                        }}>
                          {stg === "early" ? "Early" : stg === "bubble" ? "Bubble" : "Final ★"}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Summary */}
                  <div style={{ paddingTop: 12, borderTop: "1px solid rgba(216,182,90,0.1)" }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 10 }}>
                      <div style={{ width: 3, height: 14, borderRadius: 2, background: "#d8b65a" }} />
                      <span style={{ color: "#ece7d2", fontSize: "0.65rem", letterSpacing: "0.15em", textTransform: "uppercase" }}>Spot</span>
                    </div>
                    <div className="space-y-2">
                      {[
                        { label: "Spot", value: `${position} ${mode === "open" ? "open" : "vs all-in"}` },
                        { label: "Akcja", value: mode === "open" ? "Shove / Fold" : "Call / Fold", color: mode === "open" ? "#74c244" : "#d99a3a" },
                        { label: "Szerokość", value: widthPct.toFixed(1) + "%" },
                      ].map(row => (
                        <div key={row.label} className="flex justify-between" style={{ fontSize: "0.72rem" }}>
                          <span style={{ color: "#7d8ca6" }}>{row.label}</span>
                          <span style={{ color: row.color ?? "#ece7d2", fontWeight: 600 }}>{row.value}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </Card>
            </div>

            {/* CENTER — Range grid */}
            <div className="lg:col-span-6">
              <Card style={{
                background: "rgba(7,16,31,0.88)",
                backdropFilter: "blur(20px)",
                border: "1px solid rgba(216,182,90,0.18)",
                boxShadow: "0 8px 40px rgba(0,0,0,0.6), 0 0 0 1px rgba(216,182,90,0.06)",
              }} className="p-5">

                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <div style={{ width: 3, height: 14, borderRadius: 2, background: "#d8b65a" }} />
                    <span style={{ color: "#ece7d2", fontSize: "0.7rem", letterSpacing: "0.15em", textTransform: "uppercase" }}>
                      Plansza zakresów — {position} {stackDepth[0]}BB
                    </span>
                  </div>
                  {isCalculating && (
                    <span className="animate-pulse" style={{ color: "#d8b65a", fontSize: "0.65rem" }}>● przeliczam...</span>
                  )}
                </div>

                {/* 13×13 grid */}
                <div className="grid grid-cols-13 gap-[2px] mb-4">
                  {RANKS.map((_, rowIdx) =>
                    RANKS.map((__, colIdx) => {
                      const label = getHandLabel(rowIdx, colIdx);
                      const action = cellAction(rowIdx, colIdx);
                      return (
                        <button
                          key={`${rowIdx}-${colIdx}`}
                          className={`aspect-square flex items-center justify-center rounded border transition-all ${getActionColor(action)}`}
                          style={{ fontSize: "0.6rem", fontWeight: 600 }}
                        >
                          <span style={{
                            color: action === "shove" ? "#74c244" : action === "call" ? "#d99a3a" : "rgba(125,140,166,0.45)"
                          }}>{label}</span>
                        </button>
                      );
                    })
                  )}
                </div>

                {/* Legend */}
                <div className="flex gap-6 justify-center pt-3" style={{ borderTop: "1px solid rgba(216,182,90,0.1)" }}>
                  {[
                    { action: "SHOVE", color: "#74c244", bg: "rgba(116,194,68,0.15)" },
                    { action: "CALL", color: "#d99a3a", bg: "rgba(217,154,58,0.15)" },
                    { action: "FOLD", color: "rgba(125,140,166,0.5)", bg: "rgba(13,30,44,0.6)" },
                  ].map(item => (
                    <div key={item.action} className="flex items-center gap-2">
                      <div style={{ width: 14, height: 14, borderRadius: 3, background: item.bg, border: `1px solid ${item.color}` }} />
                      <span style={{ color: item.color, fontSize: "0.65rem", fontWeight: 700, letterSpacing: "0.08em" }}>{item.action}</span>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            {/* RIGHT — Hand Analysis */}
            <div className="lg:col-span-3">
              <Card style={{
                background: "rgba(7,16,31,0.88)",
                backdropFilter: "blur(20px)",
                border: "1px solid rgba(216,182,90,0.18)",
                boxShadow: "0 8px 40px rgba(0,0,0,0.6), 0 0 0 1px rgba(216,182,90,0.06)",
              }} className="p-5">
                <div className="space-y-4">

                  <div className="flex items-center gap-2 pb-3" style={{ borderBottom: "1px solid rgba(216,182,90,0.1)" }}>
                    <div style={{ width: 3, height: 14, borderRadius: 2, background: "#d8b65a" }} />
                    <span style={{ color: "#ece7d2", fontSize: "0.7rem", letterSpacing: "0.15em", textTransform: "uppercase" }}>Analiza rozdania</span>
                  </div>

                  {/* Upload */}
                  <div className="relative">
                    <input type="file" accept="image/png,image/jpeg,image/webp"
                      onChange={handleFileUpload}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-10"
                      id="file-upload"
                    />
                    <label htmlFor="file-upload" className="block cursor-pointer" style={{
                      border: "2px dashed rgba(216,182,90,0.2)",
                      borderRadius: 10, padding: "20px 12px",
                      textAlign: "center",
                      background: "rgba(3,7,15,0.4)",
                      transition: "border-color 0.2s",
                    }}>
                      {uploadedImage ? (
                        <div>
                          <img src={uploadedImage} alt="Uploaded hand" style={{ width: "100%", borderRadius: 8, marginBottom: 8 }} />
                          <Button onClick={(e) => { e.preventDefault(); setUploadedImage(null); }}
                            variant="outline" size="sm"
                            style={{ borderColor: "rgba(216,182,90,0.2)", color: "#7d8ca6", fontSize: "0.7rem" }}>
                            Wyczyść
                          </Button>
                        </div>
                      ) : (
                        <div>
                          <Upload style={{ width: 28, height: 28, margin: "0 auto 8px", color: "rgba(216,182,90,0.35)" }} />
                          <p style={{ color: "#ece7d2", fontSize: "0.8rem" }}>Wgraj screenshot</p>
                          <p style={{ color: "#7d8ca6", fontSize: "0.6rem", marginTop: 4 }}>PNG · JPG · WEBP</p>
                        </div>
                      )}
                    </label>
                  </div>

                  {/* Status */}
                  <div style={{
                    padding: "8px 12px", borderRadius: 8,
                    background: "rgba(3,7,15,0.5)",
                    border: "1px solid rgba(216,182,90,0.08)",
                  }}>
                    <p style={{ color: "#7d8ca6", fontSize: "0.7rem" }}>
                      {uploadedImage ? "✓ Zdjęcie wczytane" : "Oczekiwanie na zdjęcie..."}
                    </p>
                  </div>

                  {/* Verdict */}
                  {uploadedImage && (
                    <div style={{
                      padding: "12px",
                      borderRadius: 10,
                      background: "rgba(26,97,73,0.15)",
                      border: "1px solid rgba(116,194,68,0.35)",
                    }}>
                      <p style={{ color: "#74c244", fontSize: "0.65rem", fontWeight: 700, letterSpacing: "0.1em", marginBottom: 4 }}>✓ WERDYKT</p>
                      <p style={{ color: "#ece7d2", fontSize: "0.75rem" }}>Decyzja zgodna z zakresem Nash. Poprawne zagranie.</p>
                    </div>
                  )}

                  {/* Raise sizing placeholders */}
                  <div style={{ paddingTop: 12, borderTop: "1px solid rgba(216,182,90,0.1)", opacity: 0.45 }}>
                    <div className="flex items-center gap-2 mb-3">
                      <div style={{ width: 3, height: 14, borderRadius: 2, background: "#7d8ca6" }} />
                      <span style={{ color: "#7d8ca6", fontSize: "0.65rem", letterSpacing: "0.15em", textTransform: "uppercase" }}>Sizing raise</span>
                    </div>
                    <div className="space-y-1.5">
                      {["2.2x Small", "3x Mid", "4x Big"].map(s => (
                        <div key={s} style={{
                          padding: "8px 10px", borderRadius: 6,
                          background: "rgba(3,7,15,0.5)",
                          border: "1px solid rgba(216,182,90,0.08)",
                          color: "#7d8ca6", fontSize: "0.7rem",
                        }}>{s}</div>
                      ))}
                    </div>
                    <p style={{ color: "#7d8ca6", fontSize: "0.58rem", fontStyle: "italic", marginTop: 6 }}>dostępne przy drzewie raise / postflop</p>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>

        {/* ── TABLE SPACER — lets the felt show ── */}
        <div style={{ height: "clamp(180px, 28vw, 340px)" }} />

        {/* ── FOOTER ── */}
        <footer className="absolute bottom-4 inset-x-0 text-center" style={{ zIndex: 20 }}>
          <div className="inline-flex items-center gap-3 px-5 py-2 rounded-full" style={{
            background: "rgba(7,16,31,0.7)",
            backdropFilter: "blur(12px)",
            border: "1px solid rgba(216,182,90,0.12)",
          }}>
            <span style={{ color: "#d8b65a", fontSize: "0.6rem" }}>♠</span>
            <p style={{ color: "#7d8ca6", fontSize: "0.62rem" }}>Bunkhouse · narzędzie do nauki off-table · nie do użycia w trakcie gry</p>
            <span style={{ color: "#d8b65a", fontSize: "0.6rem" }}>♠</span>
          </div>
        </footer>
      </div>
    </div>
  );
}
