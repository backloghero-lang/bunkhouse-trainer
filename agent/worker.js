// PokerHouse — "Ziomek od Pokera" agent (Cloudflare Worker)
// Klucz API NIGDY nie jest w kodzie ani w repo — siedzi jako SECRET: env.ANTHROPIC_API_KEY
// Opcjonalny limit po IP: zbinduj KV namespace jako env.PB_KV (jak nie ma — limit pilnuje tylko front).

const SITE = "PokerHouse to strona-trening turniejowego pokera. Sekcje: ICM Trainer (zakresy push/fold), Charts (tabele push/fold przy 9-osobowym stole), Legendary Hands (filmy z legendarnymi rozdaniami), Wall of Fame, Learn (linki do szkol pokera), Hand Analyzer (analiza wlasnych rozdan z PokerStars/GGPoker). To narzedzie do nauki off-table, nie do gry na zywo ani RTA.";

function systemPrompt(lang){
  const L = lang === "pl" ? "po polsku" : lang === "es" ? "en espanol" : "in English";
  return [
    'Jestes "Ziomek od Pokera" — luzacki, przesmiewczy kumpel-czat na stronie PokerHouse.',
    "Mowisz KROTKO (max 2-3 zdania), z humorem i slangiem (\"ziom\", \"mordo\"). Odpowiadasz " + L + ".",
    "TWARDA ZASADA: rozmawiasz WYLACZNIE o pokerze i o tym co jest na tej stronie.",
    "Na cokolwiek spoza tematu reagujesz przesmiewczo i zawracasz do pokera — nie odpowiadasz merytorycznie na nic innego (matma, polityka, kod, itp.).",
    "Nie wymyslaj funkcji ktorych nie ma na stronie. Badz pomocny, ale zwiezly.",
    "Kontekst strony: " + SITE
  ].join("\n");
}

function J(obj, status, cors){ return new Response(JSON.stringify(obj), {status:status, headers:Object.assign({"Content-Type":"application/json"}, cors)}); }

export default {
  async fetch(request, env){
    const cors = {
      "Access-Control-Allow-Origin": env.ALLOW_ORIGIN || "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    };
    if (request.method === "OPTIONS") return new Response(null, {headers: cors});
    if (request.method !== "POST") return J({error:"POST only"}, 405, cors);

    let body;
    try { body = await request.json(); } catch(e){ return J({error:"bad json"}, 400, cors); }
    const msg = (body.message || "").toString().slice(0, 500).trim();
    const lang = ["pl","en","es"].includes(body.lang) ? body.lang : "en";
    if (!msg) return J({error:"empty"}, 400, cors);

    const LIMIT = parseInt(env.DAILY_LIMIT || "5", 10);
    const ip = request.headers.get("CF-Connecting-IP") || "anon";
    const day = new Date().toISOString().slice(0,10);
    const key = "q:" + ip + ":" + day;
    let used = 0;
    if (env.PB_KV){
      used = parseInt((await env.PB_KV.get(key)) || "0", 10);
      if (used >= LIMIT) return J({reply:null, limited:true, remaining:0}, 200, cors);
    }

    let r;
    try {
      r = await fetch("https://api.anthropic.com/v1/messages", {
        method:"POST",
        headers:{ "Content-Type":"application/json", "x-api-key": env.ANTHROPIC_API_KEY, "anthropic-version":"2023-06-01" },
        body: JSON.stringify({
          model: "claude-haiku-4-5-20251001",
          max_tokens: 300,
          system: systemPrompt(lang),
          messages: [{ role:"user", content: msg }]
        })
      });
    } catch(e){ return J({error:"network"}, 502, cors); }
    if (!r.ok) return J({error:"upstream", status:r.status}, 502, cors);

    const data = await r.json();
    const reply = (data.content && data.content[0] && data.content[0].text) ? data.content[0].text : "";

    let remaining = null;
    if (env.PB_KV){
      await env.PB_KV.put(key, String(used+1), {expirationTtl: 90000});
      remaining = Math.max(0, LIMIT - (used+1));
    }
    return J({reply: reply, remaining: remaining}, 200, cors);
  }
}
