// Atom Edu, Cloudflare Worker with analytics.
//
// Secrets (set via `wrangler secret put`):
//   GROQ_API_KEY     Groq bearer token
//   ADMIN_PASSWORD   password gating /api/admin/stats
//   ENCRYPTION_KEY   optional, base64 32-byte key for AES-GCM (unchanged)
//
// Public env (wrangler.toml [vars]):
//   ALLOWED_ORIGIN   the origin(s) allowed to call this Worker (comma separated)
//   GROQ_ENDPOINT    defaults to Groq's OpenAI-compatible endpoint
//   DAILY_CAP        per-email drafts per day (default 5) for the capped model
//
// KV binding required for analytics + rate limit:
//   RATE_KV          bind a KV namespace in wrangler.toml
//
// Analytics keys stored in KV:
//   stat:total                       running total drafts count
//   stat:day:YYYY-MM-DD              per-day count
//   stat:model:<model>               per-model count
//   stat:domain:<school.edu>         per-domain count
//   stat:err:count                   error count today
//   stat:err:day:YYYY-MM-DD          errors per day
//   stat:email:<email>               1, used for unique teacher count
//   stat:emails                      set-like list (JSON array)
//   stat:recent                      last 10 activities (JSON array)

const GROQ_DEFAULT = "https://api.groq.com/openai/v1/chat/completions";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const allowed = env.ALLOWED_ORIGIN || "*";

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin, allowed) });
    }

    try {
      if (url.pathname === "/api/health") {
        return json({
          ok: true,
          hasGroqKey: !!env.GROQ_API_KEY,
          hasAdminPw: !!env.ADMIN_PASSWORD,
          hasKV: !!env.RATE_KV,
        }, origin, allowed);
      }

      if (url.pathname === "/api/groq" && request.method === "POST") {
        return await handleGroq(request, env, origin, allowed);
      }

      if (url.pathname === "/api/admin/stats" && request.method === "POST") {
        return await handleAdminStats(request, env, origin, allowed);
      }

      if (url.pathname === "/api/encrypt" && request.method === "POST") {
        if (!env.ENCRYPTION_KEY) return json({ error: "Server missing ENCRYPTION_KEY" }, origin, allowed, 500);
        const { plaintext } = await request.json();
        if (typeof plaintext !== "string") return json({ error: "plaintext required" }, origin, allowed, 400);
        const out = await encryptAesGcm(env.ENCRYPTION_KEY, plaintext);
        return json(out, origin, allowed);
      }
      if (url.pathname === "/api/decrypt" && request.method === "POST") {
        if (!env.ENCRYPTION_KEY) return json({ error: "Server missing ENCRYPTION_KEY" }, origin, allowed, 500);
        const { iv, ciphertext } = await request.json();
        if (!iv || !ciphertext) return json({ error: "iv+ciphertext required" }, origin, allowed, 400);
        const plaintext = await decryptAesGcm(env.ENCRYPTION_KEY, iv, ciphertext);
        return json({ plaintext }, origin, allowed);
      }


      if (url.pathname === "/api/presenton/generate" && request.method === "POST") {
        return await handlePresentonGenerate(request, env, origin, allowed);
      }

      if (url.pathname === "/api/presenton/status" && request.method === "POST") {
        return await handlePresentonStatus(request, env, origin, allowed);
      }

      return json({ error: "Not found" }, origin, allowed, 404);
    } catch (e) {
      return json({ error: e.message || String(e) }, origin, allowed, 500);
    }
  },
};

async function handleGroq(request, env, origin, allowed) {
  if (!env.GROQ_API_KEY) return json({ error: "Server missing GROQ_API_KEY" }, origin, allowed, 500);
  const body = await request.json();
  if (!body || !body.model || !Array.isArray(body.messages)) {
    return json({ error: "Bad request" }, origin, allowed, 400);
  }
  const cap = parseInt(env.DAILY_CAP || "5", 10);
  const email = (body.email || "").toLowerCase();
  if (!email || !/^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.(edu|org)$/.test(email)) {
    return json({ error: "email required and must be .edu or .org" }, origin, allowed, 403);
  }
  const day = new Date().toISOString().slice(0, 10);
  const domain = email.split("@")[1] || "unknown";

  if (body.model === "openai/gpt-oss-120b" && env.RATE_KV) {
    const key = `rl:${email}:${day}`;
    const cur = parseInt((await env.RATE_KV.get(key)) || "0", 10);
    if (cur >= cap) return json({ error: "Daily cap reached", cap }, origin, allowed, 429);
    await env.RATE_KV.put(key, String(cur + 1), { expirationTtl: 172800 });
  }

  const upstreamBody = {
    model: body.model,
    messages: body.messages,
    temperature: body.temperature ?? 0.5,
    max_tokens: Math.min(body.max_tokens ?? 2048, 8192),
  };
  if (body.response_format) upstreamBody.response_format = body.response_format;

  const endpoint = env.GROQ_ENDPOINT || GROQ_DEFAULT;
  const upstream = await fetch(endpoint, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${env.GROQ_API_KEY}`,
    },
    body: JSON.stringify(upstreamBody),
  });

  const ok = upstream.ok;
  const upstreamJson = ok ? await upstream.json() : { error: await upstream.text() };
  const content = ok ? (upstreamJson.choices?.[0]?.message?.content ?? "") : "";
  const tool = pickTool(body.messages);

  if (env.RATE_KV) {
    await trackDraft(env.RATE_KV, {
      email,
      domain,
      day,
      model: body.model,
      tool,
      ok,
    });
  }

  if (!ok) {
    return json({ error: `Groq ${upstream.status}`, detail: String(upstreamJson.error).slice(0, 500) }, origin, allowed, 502);
  }
  return json({ content, usage: upstreamJson.usage || null, model: body.model }, origin, allowed);
}


const PRESENTON_API = "https://api.presenton.ai/api/v3";

async function handlePresentonGenerate(request, env, origin, allowed) {
  if (!env.PRESENTON_API_KEY) return json({ error: "Server missing PRESENTON_API_KEY" }, origin, allowed, 500);
  const body = await request.json();
  // Anyone can export a slideshow. Email is used only for analytics, not gating.
  const email = (body.email || "anonymous@atom-edu.org").toLowerCase();
  const content = body.content || "";
  if (!content) return json({ error: "content required" }, origin, allowed, 400);

  // Clamp slide count to protect the credit balance (2 credits/slide).
  const nSlides = Math.max(3, Math.min(parseInt(body.n_slides || 5, 10) || 5, 8));
  const payload = {
    content: content,
    n_slides: nSlides,
    tone: "educational",
    language: "English",
    export_as: "pptx",
    include_title_slide: true,
    speaker_notes: true,
    verbosity: "standard"
  };

  const upstream = await fetch(PRESENTON_API + "/presentation/generate/async", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + env.PRESENTON_API_KEY,
    },
    body: JSON.stringify(payload),
  });

  const data = await upstream.json();
  if (!upstream.ok) {
    return json({ error: "Presenton error", detail: JSON.stringify(data).slice(0, 500) }, origin, allowed, 502);
  }

  // Track in analytics
  if (env.RATE_KV) {
    const day = new Date().toISOString().slice(0, 10);
    const domain = email.split("@")[1] || "unknown";
    await trackDraft(env.RATE_KV, { email, domain, day, model: "presenton", tool: "Slideshow", ok: true });
  }

  // Forward full response so frontend can find the right field
  return json(data, origin, allowed);
}

async function handlePresentonStatus(request, env, origin, allowed) {
  if (!env.PRESENTON_API_KEY) return json({ error: "Server missing PRESENTON_API_KEY" }, origin, allowed, 500);
  const body = await request.json();
  const taskId = body.task_id;
  if (!taskId) return json({ error: "task_id required" }, origin, allowed, 400);

  const upstream = await fetch(PRESENTON_API + "/async-task/status/" + encodeURIComponent(taskId), {
    method: "GET",
    headers: {
      "Authorization": "Bearer " + env.PRESENTON_API_KEY,
    },
  });

  const data = await upstream.json();
  if (!upstream.ok) {
    return json({ error: "Presenton status error", detail: JSON.stringify(data).slice(0, 500) }, origin, allowed, 502);
  }

  return json(data, origin, allowed);
}

function pickTool(messages) {
  const sys = (messages.find(m => m.role === "system")?.content || "").toLowerCase();
  if (sys.includes("worksheet")) return "Assignment";
  if (sys.includes("quiz")) return "Quiz";
  if (sys.includes("rubric")) return "Rubric";
  if (sys.includes("lesson plan")) return "Lesson";
  if (sys.includes("reading passage")) return "Passage";
  if (sys.includes("slide")) return "Slides";
  if (sys.includes("note home")) return "Note home";
  if (sys.includes("adapt")) return "Differentiation";
  return "Draft";
}

async function trackDraft(kv, e) {
  try {
    const inc = async (k, by = 1) => {
      const cur = parseInt((await kv.get(k)) || "0", 10);
      await kv.put(k, String(cur + by));
    };
    await inc("stat:total");
    await inc(`stat:day:${e.day}`);
    await inc(`stat:model:${e.model}`);
    await inc(`stat:domain:${e.domain}`);
    if (!e.ok) {
      await inc("stat:err:count");
      await inc(`stat:err:day:${e.day}`);
    }
    const seen = await kv.get(`stat:email:${e.email}`);
    if (!seen) {
      await kv.put(`stat:email:${e.email}`, "1");
      const list = JSON.parse((await kv.get("stat:emails")) || "[]");
      list.push(e.email);
      await kv.put("stat:emails", JSON.stringify(list.slice(-5000)));
    }
    const recent = JSON.parse((await kv.get("stat:recent")) || "[]");
    recent.unshift({ email: e.email, tool: e.tool, ok: e.ok, ts: Date.now() });
    await kv.put("stat:recent", JSON.stringify(recent.slice(0, 20)));
  } catch (_) {
    // analytics are best effort
  }
}

async function handleAdminStats(request, env, origin, allowed) {
  const { password } = await request.json();
  if (!env.ADMIN_PASSWORD) return json({ error: "Server missing ADMIN_PASSWORD" }, origin, allowed, 500);
  if (!password || password !== env.ADMIN_PASSWORD) {
    return json({ error: "Wrong password" }, origin, allowed, 401);
  }
  if (!env.RATE_KV) return json({ error: "KV not bound" }, origin, allowed, 500);

  const kv = env.RATE_KV;
  const now = new Date();
  const today = now.toISOString().slice(0, 10);
  const totalDrafts = parseInt((await kv.get("stat:total")) || "0", 10);
  const draftsToday = parseInt((await kv.get(`stat:day:${today}`)) || "0", 10);

  // Weekly: last 7 days including today.
  const weekly = [];
  for (let i = 6; i >= 0; i--) {
    const d = new Date(now.getTime() - i * 86400000).toISOString().slice(0, 10);
    weekly.push(parseInt((await kv.get(`stat:day:${d}`)) || "0", 10));
  }

  // Emails.
  const emails = JSON.parse((await kv.get("stat:emails")) || "[]");
  const teachers = emails.length;

  // Models.
  const models = await pickCounters(kv, "stat:model:");
  // Domains.
  const domains = await pickCounters(kv, "stat:domain:");

  // Error rate today.
  const errToday = parseInt((await kv.get(`stat:err:day:${today}`)) || "0", 10);
  const errorRate = draftsToday > 0 ? errToday / draftsToday : 0;

  // Recent.
  const recent = JSON.parse((await kv.get("stat:recent")) || "[]");

  return json({
    totalDrafts, draftsToday, teachers, errorRate,
    weekly, models, domains, recent,
  }, origin, allowed);
}

async function pickCounters(kv, prefix) {
  const out = {};
  let cursor;
  for (;;) {
    const res = await kv.list({ prefix, cursor });
    for (const k of res.keys) {
      out[k.name.slice(prefix.length)] = parseInt((await kv.get(k.name)) || "0", 10);
    }
    if (res.list_complete) break;
    cursor = res.cursor;
  }
  return out;
}

function corsHeaders(origin, allowed) {
  const list = (allowed || "*").split(",").map(s => s.trim());
  const ok = list.includes("*") || list.includes(origin);
  return {
    "Access-Control-Allow-Origin": ok ? origin : list[0],
    "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Max-Age": "86400",
    "Vary": "Origin",
  };
}

function json(obj, origin, allowed, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", ...corsHeaders(origin, allowed) },
  });
}

async function importKey(b64) {
  const raw = b64ToBytes(b64);
  if (raw.length !== 32) throw new Error("ENCRYPTION_KEY must be base64 of 32 bytes (256-bit)");
  return crypto.subtle.importKey("raw", raw, { name: "AES-GCM" }, false, ["encrypt", "decrypt"]);
}
async function encryptAesGcm(keyB64, plaintext) {
  const key = await importKey(keyB64);
  const iv = crypto.getRandomValues(new Uint8Array(12));
  const ct = await crypto.subtle.encrypt({ name: "AES-GCM", iv }, key, new TextEncoder().encode(plaintext));
  return { iv: bytesToB64(iv), ciphertext: bytesToB64(new Uint8Array(ct)) };
}
async function decryptAesGcm(keyB64, ivB64, ctB64) {
  const key = await importKey(keyB64);
  const pt = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: b64ToBytes(ivB64) },
    key,
    b64ToBytes(ctB64)
  );
  return new TextDecoder().decode(pt);
}
function b64ToBytes(b64) {
  const s = atob(b64);
  const a = new Uint8Array(s.length);
  for (let i = 0; i < s.length; i++) a[i] = s.charCodeAt(i);
  return a;
}
function bytesToB64(bytes) {
  let s = "";
  for (let i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]);
  return btoa(s);
}
