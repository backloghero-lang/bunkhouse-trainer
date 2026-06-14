// PokerHouse — "Ziomek od Pokera" (Cloudflare Worker + Google Gemini)
// Klucz NIGDY w kodzie/repo: secret env.GEMINI_API_KEY (z Google AI Studio).
// Prompt edytowalny w repo: agent/prompt.txt (Worker go zaciąga z PROMPT_URL).
// Parametry sterowane zmiennymi: MODEL, TEMPERATURE, MAX_TOKENS, THINKING_BUDGET, DAILY_LIMIT, ALLOW_ORIGIN.

const DEFAULT_PROMPT_URL = "https://raw.githubusercontent.com/backloghero-lang/bunkhouse-trainer/main/agent/prompt.txt";
const FALLBACK_PROMPT = "Jestes 'Ziomek od Pokera' - wyluzowany, przesmiewczy czat na stronie PokerHouse. Rozmawiasz tylko o pokerze i o tej stronie (ICM Trainer, Charts, Legendary Hands, Wall of Fame, Learn, Hand Analyzer). Na off-topic reagujesz przesmiewczo i zawracasz do pokera. Krotko (2-3 zdania). Odpowiadasz {{LANG}}.";

let _cache = { text: null, at: 0 };
async function getPrompt(env){
  const url = env.PROMPT_URL || DEFAULT_PROMPT_URL;
  const now = Date.now();
  if (_cache.text && (now - _cache.at) < 60000) return _cache.text;
  try {
    const r = await fetch(url, { cf: { cacheTtl: 60, cacheEverything: true } });
    if (r.ok) { const t = await r.text(); if (t && t.trim()) { _cache = { text: t, at: now }; return t; } }
  } catch (e) {}
  return _cache.text || FALLBACK_PROMPT;
}
function langName(l){ return l === "pl" ? "po polsku" : l === "es" ? "en espanol" : "in English"; }
function J(obj, status, cors){ return new Response(JSON.stringify(obj), { status: status, headers: Object.assign({ "Content-Type": "application/json" }, cors) }); }

export default {
  async fetch(request, env){
    const cors = {
      "Access-Control-Allow-Origin": env.ALLOW_ORIGIN || "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });
    if (request.method !== "POST") return J({ error: "POST only" }, 405, cors);

    let body;
    try { body = await request.json(); } catch (e) { return J({ error: "bad json" }, 400, cors); }
    const msg = (body.message || "").toString().slice(0, 500).trim();
    const lang = ["pl","en","es"].includes(body.lang) ? body.lang : "en";
    if (!msg) return J({ error: "empty" }, 400, cors);

    const LIMIT = parseInt(env.DAILY_LIMIT || "5", 10);
    const ip = request.headers.get("CF-Connecting-IP") || "anon";
    const key = "q:" + ip + ":" + new Date().toISOString().slice(0,10);
    let used = 0;
    if (env.PB_KV) {
      used = parseInt((await env.PB_KV.get(key)) || "0", 10);
      if (used >= LIMIT) return J({ reply: null, limited: true, remaining: 0 }, 200, cors);
    }

    const system = (await getPrompt(env)).replace(/\{\{\s*LANG\s*\}\}/g, langName(lang));
    const model = env.MODEL || "gemini-2.5-flash";
    const genCfg = {
      temperature: parseFloat(env.TEMPERATURE || "0.85"),
      maxOutputTokens: parseInt(env.MAX_TOKENS || "320", 10),
      thinkingConfig: { thinkingBudget: parseInt(env.THINKING_BUDGET || "512", 10) }
    };
    const url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + env.GEMINI_API_KEY;

    let r;
    try {
      r = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          systemInstruction: { parts: [{ text: system }] },
          contents: [{ role: "user", parts: [{ text: msg }] }],
          generationConfig: genCfg
        })
      });
    } catch (e) { return J({ error: "network" }, 502, cors); }
    if (!r.ok) return J({ error: "upstream", status: r.status, detail: (await r.text()).slice(0,300) }, 502, cors);

    const data = await r.json();
    let reply = "";
    try { reply = data.candidates[0].content.parts.map(function(p){ return p.text || ""; }).join("").trim(); } catch (e) {}
    if (!reply) reply = "";

    let remaining = null;
    if (env.PB_KV) { await env.PB_KV.put(key, String(used + 1), { expirationTtl: 90000 }); remaining = Math.max(0, LIMIT - (used + 1)); }
    return J({ reply: reply, remaining: remaining }, 200, cors);
  }
}
