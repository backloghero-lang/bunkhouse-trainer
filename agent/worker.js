// PokerHouse — "Bullet Bot" (Cloudflare Worker + Google Gemini)
// Sekrety: GEMINI_API_KEY (wymagany), opcjonalnie DEV_KEY (Twoje obejście limitu).
// Prompt edytowalny w repo: agent/prompt.txt (Worker go zaciąga z PROMPT_URL).
// Zmienne: MODEL, TEMPERATURE, MAX_TOKENS, THINKING_BUDGET, DAILY_LIMIT, ALLOW_ORIGIN, DEV_KEY.

const DEFAULT_PROMPT_URL = "https://raw.githubusercontent.com/backloghero-lang/bunkhouse-trainer/main/agent/prompt.txt";
const FALLBACK_PROMPT = "Jestes 'Bullet Bot' - bystry, sarkastyczny asystent na stronie PokerHouse. Gadasz o pokerze turniejowym, ICM, Nash, push/fold, MTT, bankrollu i o sekcjach strony (ICM Trainer, Charts, Legendary Hands, Wall of Fame, Learn, Hand Analyzer). Na off-topic zbywasz sarkastycznie. Najpierw krotki ironiczny komentarz, potem konkret. Odpowiadasz {{LANG}}.";

let _cache = { text: null, at: 0 };
async function getPrompt(env){
  const url = env.PROMPT_URL || DEFAULT_PROMPT_URL;
  const now = Date.now();
  if (_cache.text && (now - _cache.at) < 60000) return _cache.text;
  try { const r = await fetch(url, { cf: { cacheTtl: 60, cacheEverything: true } });
    if (r.ok){ const t = await r.text(); if (t && t.trim()){ _cache = { text:t, at:now }; return t; } } } catch(e){}
  return _cache.text || FALLBACK_PROMPT;
}
function langName(l){ return l==="pl"?"po polsku":l==="es"?"en espanol":"in English"; }
function J(obj, status, cors){ return new Response(JSON.stringify(obj), { status:status, headers:Object.assign({ "Content-Type":"application/json" }, cors) }); }

export default {
  async fetch(request, env){
    const cors = { "Access-Control-Allow-Origin": env.ALLOW_ORIGIN || "*", "Access-Control-Allow-Methods":"POST, OPTIONS", "Access-Control-Allow-Headers":"Content-Type" };
    if (request.method === "OPTIONS") return new Response(null, { headers: cors });
    if (request.method !== "POST") return J({ error:"POST only" }, 405, cors);

    let body; try { body = await request.json(); } catch(e){ return J({ error:"bad json" }, 400, cors); }
    const msg = (body.message || "").toString().slice(0, 600).trim();
    const lang = ["pl","en","es"].includes(body.lang) ? body.lang : "en";
    if (!msg) return J({ error:"empty" }, 400, cors);

    // Obejscie limitu dla wlasciciela (klucz w body.dev == env.DEV_KEY)
    const owner = !!(env.DEV_KEY && body.dev && body.dev.toString() === env.DEV_KEY);

    const LIMIT = parseInt(env.DAILY_LIMIT || "5", 10);
    const ip = request.headers.get("CF-Connecting-IP") || "anon";
    const key = "q:" + ip + ":" + new Date().toISOString().slice(0,10);
    let used = 0;
    if (!owner && env.PB_KV){
      used = parseInt((await env.PB_KV.get(key)) || "0", 10);
      if (used >= LIMIT) return J({ reply:null, limited:true, remaining:0 }, 200, cors);
    }

    // Historia rozmowy (pamiec watku) -> contents
    const hist = Array.isArray(body.history) ? body.history.slice(-12) : [];
    const contents = [];
    for (let i=0;i<hist.length;i++){ const h=hist[i]; if (h && h.text){ contents.push({ role: h.role==="model"?"model":"user", parts:[{ text:String(h.text).slice(0,1200) }] }); } }
    contents.push({ role:"user", parts:[{ text: msg }] });

    const system = (await getPrompt(env)).replace(/\{\{\s*LANG\s*\}\}/g, langName(lang));
    const model = env.MODEL || "gemini-2.5-flash";
    const genCfg = { temperature: parseFloat(env.TEMPERATURE || "0.85"), maxOutputTokens: parseInt(env.MAX_TOKENS || "700", 10), thinkingConfig: { thinkingBudget: parseInt(env.THINKING_BUDGET || "0", 10) } };
    const url = "https://generativelanguage.googleapis.com/v1beta/models/" + model + ":generateContent?key=" + env.GEMINI_API_KEY;

    let r; try {
      r = await fetch(url, { method:"POST", headers:{ "Content-Type":"application/json" },
        body: JSON.stringify({ systemInstruction:{ parts:[{ text: system }] }, contents: contents, generationConfig: genCfg }) });
    } catch(e){ return J({ error:"network" }, 502, cors); }
    if (!r.ok) return J({ error:"upstream", status:r.status, detail:(await r.text()).slice(0,300) }, 502, cors);

    const data = await r.json();
    let reply = "";
    try { reply = data.candidates[0].content.parts.map(function(p){ return p.text||""; }).join("").trim(); } catch(e){}

    let remaining = null;
    if (!owner && env.PB_KV){ await env.PB_KV.put(key, String(used+1), { expirationTtl:90000 }); remaining = Math.max(0, LIMIT-(used+1)); }
    return J({ reply: reply, remaining: remaining, owner: owner }, 200, cors);
  }
}
