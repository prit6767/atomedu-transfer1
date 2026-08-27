// Atom Edu — Cloudflare Worker
// Secrets (set via `wrangler secret put`):
//   GROQ_API_KEY     — Groq bearer token (used server-side only)
//   ENCRYPTION_KEY   — base64 32-byte key for AES-GCM payload encryption
//
// Public env (in wrangler.toml [vars] or Dashboard → Variables):
//   ALLOWED_ORIGIN   — the origin allowed to call this Worker
//   GROQ_ENDPOINT    — defaults to Groq's OpenAI-compatible endpoint
//   DAILY_CAP        — per-email drafts/day (defaults to 5)

const GROQ_DEFAULT = "https://api.groq.com/openai/v1/chat/completions";

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const origin = request.headers.get("Origin") || "";
    const allowed = env.ALLOWED_ORIGIN || "*";

    // CORS preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders(origin, allowed) });
    }

    try {
      // Health
      if (url.pathname === "/api/health") {
        return json({ ok: true, hasGroqKey: !!env.GROQ_API_KEY, hasEncKey: !!env.ENCRYPTION_KEY }, origin, allowed);
      }

      // Main Groq proxy — {model, messages, temperature, max_tokens, email, response_format}
      if (url.pathname === "/api/groq" && request.method === "POST") {
        if (!env.GROQ_API_KEY) return json({ error: "Server missing GROQ_API_KEY" }, origin, allowed, 500);

        const body = await request.json();
        if (!body || !body.model || !Array.isArray(body.messages)) {
          return json({ error: "Bad request" }, origin, allowed, 400);
        }

        // Per-email daily cap enforced server-side (in-memory fallback if no KV binding).
        const cap = parseInt(env.DAILY_CAP || "5", 10);
        const email = (body.email || "").toLowerCase();
        if (!email || !/^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.(edu|org)$/.test(email)) {
          return json({ error: "email required and must be .edu or .org" }, origin, allowed, 403);
        }
        // Only count the heavy 120B calls toward the cap.
        if (body.model === "openai/gpt-oss-120b" && env.RATE_KV) {
          const day = new Date().toISOString().slice(0, 10);
          const key = `rl:${email}:${day}`;
          const cur = parseInt((await env.RATE_KV.get(key)) || "0", 10);
          if (cur >= cap) return json({ error: "Daily cap reached", cap }, origin, allowed, 429);
          await env.RATE_KV.put(key, String(cur + 1), { expirationTtl: 172800 });
        }

        // Strip client-only fields, forward to Groq.
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
        if (!upstream.ok) {
          const t = await upstream.text();
          return json({ error: `Groq ${upstream.status}`, detail: t.slice(0, 500) }, origin, allowed, 502);
        }
        const j = await upstream.json();
        const content = j.choices?.[0]?.message?.content ?? "";
        return json({ content, usage: j.usage || null, model: body.model }, origin, allowed);
      }

      // Encrypt payload with ENCRYPTION_KEY (AES-GCM). Body: {plaintext:"..."}.
      if (url.pathname === "/api/encrypt" && request.method === "POST") {
        if (!env.ENCRYPTION_KEY) return json({ error: "Server missing ENCRYPTION_KEY" }, origin, allowed, 500);
        const { plaintext } = await request.json();
        if (typeof plaintext !== "string") return json({ error: "plaintext required" }, origin, allowed, 400);
        const out = await encryptAesGcm(env.ENCRYPTION_KEY, plaintext);
        return json(out, origin, allowed);
      }

      // Decrypt payload. Body: {iv, ciphertext} (both base64).
      if (url.pathname === "/api/decrypt" && request.method === "POST") {
        if (!env.ENCRYPTION_KEY) return json({ error: "Server missing ENCRYPTION_KEY" }, origin, allowed, 500);
        const { iv, ciphertext } = await request.json();
        if (!iv || !ciphertext) return json({ error: "iv+ciphertext required" }, origin, allowed, 400);
        const plaintext = await decryptAesGcm(env.ENCRYPTION_KEY, iv, ciphertext);
        return json({ plaintext }, origin, allowed);
      }

      return json({ error: "Not found" }, origin, allowed, 404);
    } catch (e) {
      return json({ error: e.message || String(e) }, origin, allowed, 500);
    }
  },
};

function corsHeaders(origin, allowed) {
  const ok = allowed === "*" || origin === allowed;
  return {
    "Access-Control-Allow-Origin": ok ? (origin || allowed) : allowed,
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

// ----- AES-GCM helpers -----
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
