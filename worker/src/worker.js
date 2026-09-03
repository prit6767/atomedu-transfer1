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
          hasGoogleId: !!env.GOOGLE_CLIENT_ID,
          hasGoogleSecret: !!env.GOOGLE_CLIENT_SECRET,
          hasPresenton: !!env.PRESENTON_API_KEY,
        }, origin, allowed);
      }

      if (url.pathname === "/api/groq" && request.method === "POST") {
        return await handleGroq(request, env, origin, allowed);
      }

      if (url.pathname === "/api/admin/stats" && request.method === "POST") {
        return await handleAdminStats(request, env, origin, allowed);
      }
      if (url.pathname === "/api/admin/delete-user" && request.method === "POST") {
        return await handleAdminDeleteUser(request, env, origin, allowed);
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

      if (url.pathname === "/api/presenton/preview" && request.method === "GET") {
        return await handlePresentonPreview(url, env, origin, allowed);
      }

      if (url.pathname === "/api/google/prepare" && request.method === "POST") {
        return await handleGooglePrepare(request, env, origin, allowed);
      }

      if (url.pathname === "/api/google/callback" && request.method === "GET") {
        return await handleGoogleCallback(request, env, url);
      }

      if (url.pathname === "/api/google/debug" && request.method === "GET") {
        return await handleGoogleDebug(request, env, url, origin, allowed);
      }

      if (url.pathname === "/lti/jwks" && request.method === "GET") {
        return await handleLtiJwks(env, origin, allowed);
      }
      if (url.pathname === "/lti/login") {
        return await handleLtiLogin(request, env, url);
      }
      if (url.pathname === "/lti/launch" && request.method === "POST") {
        return await handleLtiLaunch(request, env, url);
      }
      if (url.pathname === "/lti/session" && request.method === "POST") {
        return await handleLtiSession(request, env, origin, allowed);
      }
      if (url.pathname === "/lti/register") {
        return await handleLtiRegister(request, env, url);
      }
      if (url.pathname === "/lti/config" && request.method === "GET") {
        return handleLtiConfig(env, url);
      }

      return json({ error: "Not found" }, origin, allowed, 404);
    } catch (e) {
      return json({ error: e.message || String(e) }, origin, allowed, 500);
    }
  },
};

async function kvCount(kv, key) { return parseInt((await kv.get(key)) || "0", 10); }
async function kvBump(kv, key, ttl) { const n = (parseInt((await kv.get(key)) || "0", 10)) + 1; await kv.put(key, String(n), { expirationTtl: ttl }); return n; }

async function handleGroq(request, env, origin, allowed) {
  if (!env.GROQ_API_KEY) return json({ error: "Server missing GROQ_API_KEY" }, origin, allowed, 500);
  const body = await request.json();
  if (!body || !body.model || !Array.isArray(body.messages)) {
    return json({ error: "Bad request" }, origin, allowed, 400);
  }
  let ltiOk = false, ltiPayload = null;
  if (body.lti_session) {
    ltiPayload = await verifyToolJwt(env, body.lti_session);
    if (ltiPayload && ltiPayload.lti) ltiOk = true;
  }
  const email = (body.email || (ltiPayload && ltiPayload.email) || "").toLowerCase();
  if (!ltiOk && (!email || !/^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.(edu|org)$/.test(email))) {
    return json({ error: "email required and must be .edu or .org" }, origin, allowed, 403);
  }
  const day = new Date().toISOString().slice(0, 10);
  const rlId = email || ("lti:" + ((ltiPayload && ltiPayload.sub) || "anon"));
  const domain = email.split("@")[1] || (ltiOk ? "lti" : "unknown");

  // ---- Cost controls (all tools + models) ----------------------------------
  const isPremium = body.model === "openai/gpt-oss-120b";
  const perCap = isPremium ? parseInt(env.DAILY_CAP || "5", 10) : parseInt(env.TEXT_DAILY_CAP || "15", 10);
  const globalCap = parseInt(env.GLOBAL_DAILY_CAP || "500", 10);
  const ipCap = parseInt(env.IP_DAILY_CAP || "150", 10);
  const ip = request.headers.get("CF-Connecting-IP") || "";
  let remaining = null;
  if (env.RATE_KV) {
    if (await kvCount(env.RATE_KV, `rlg:${day}`) >= globalCap) {
      return json({ error: "Atom is at capacity for today. Please try again tomorrow.", scope: "global" }, origin, allowed, 429);
    }
    if (ip && (await kvCount(env.RATE_KV, `rlip:${ip}:${day}`)) >= ipCap) {
      return json({ error: "Too many requests from this network today. Please try again tomorrow.", scope: "ip" }, origin, allowed, 429);
    }
    const teacherKey = `rl:${rlId}:${day}`;
    const cur = await kvCount(env.RATE_KV, teacherKey);
    if (cur >= perCap) {
      return json({ error: "You've used all " + perCap + " of today's drafts. They reset tomorrow.", cap: perCap, scope: "teacher" }, origin, allowed, 429);
    }
    await kvBump(env.RATE_KV, teacherKey, 172800);
    await kvBump(env.RATE_KV, `rlg:${day}`, 172800);
    if (ip) await kvBump(env.RATE_KV, `rlip:${ip}:${day}`, 172800);
    remaining = Math.max(0, perCap - (cur + 1));
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
      email: email || rlId,
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
  return json({ content, usage: upstreamJson.usage || null, model: body.model, remaining }, origin, allowed);
}


// Presenton's documented asynchronous endpoints return a task immediately and
// provide the finished file plus editor URL through the status endpoint.
const PRESENTON_API = "https://api.presenton.ai/api/v1/ppt";

async function handlePresentonGenerate(request, env, origin, allowed) {
  if (!env.PRESENTON_API_KEY) return json({ error: "Server missing PRESENTON_API_KEY" }, origin, allowed, 500);
  const body = await request.json();
  const content = body.content || "";
  if (!content) return json({ error: "content required" }, origin, allowed, 400);

  // Slideshows cost real credits (2/slide): require a signed-in teacher and cap them.
  let ltiPayload = null;
  if (body.lti_session) { ltiPayload = await verifyToolJwt(env, body.lti_session); }
  const ltiOk = !!(ltiPayload && ltiPayload.lti);
  const email = (body.email || (ltiPayload && ltiPayload.email) || "").toLowerCase();
  const emailOk = /^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.(edu|org)$/.test(email);
  if (!ltiOk && !emailOk) {
    return json({ error: "Please sign in with your school email to export a slideshow." }, origin, allowed, 403);
  }
  const id = emailOk ? email : ("lti:" + ((ltiPayload && ltiPayload.sub) || "anon"));
  const day = new Date().toISOString().slice(0, 10);
  const month = new Date().toISOString().slice(0, 7);
  const perMonthCap = parseInt(env.SLIDES_MONTHLY_CAP || "3", 10);
  const globalDayCap = parseInt(env.GLOBAL_SLIDES_DAILY_CAP || "30", 10);
  if (env.RATE_KV) {
    if (await kvCount(env.RATE_KV, `slg:${day}`) >= globalDayCap) {
      return json({ error: "Slideshow exports are at capacity for today. Please try again tomorrow.", scope: "global" }, origin, allowed, 429);
    }
    const key = `sl:${id}:${month}`;
    if (await kvCount(env.RATE_KV, key) >= perMonthCap) {
      return json({ error: "You've used all " + perMonthCap + " slideshow exports this month. Worksheets, quizzes, and other drafts still work within your daily limit.", cap: perMonthCap, scope: "teacher" }, origin, allowed, 429);
    }
    await kvBump(env.RATE_KV, key, 60 * 60 * 24 * 40);
    await kvBump(env.RATE_KV, `slg:${day}`, 172800);
  }

  // Credit-safe slide count (default 4, hard max 6).
  const nSlides = Math.max(3, Math.min(parseInt(body.n_slides || 4, 10) || 4, 6));
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

  if (env.RATE_KV) {
    const domain = email.split("@")[1] || (ltiOk ? "lti" : "unknown");
    await trackDraft(env.RATE_KV, { email: email || id, domain, day, model: "presenton", tool: "Slideshow", ok: true });
  }

  return json(data, origin, allowed);
}

async function handlePresentonStatus(request, env, origin, allowed) {
  if (!env.PRESENTON_API_KEY) return json({ error: "Server missing PRESENTON_API_KEY" }, origin, allowed, 500);
  const body = await request.json();
  const taskId = body.task_id;
  if (!taskId) return json({ error: "task_id required" }, origin, allowed, 400);

  const upstream = await fetch(PRESENTON_API + "/presentation/status/" + encodeURIComponent(taskId), {
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

async function handlePresentonPreview(url, env, origin, allowed) {
  if (!env.PRESENTON_API_KEY) return json({ error: "Server missing PRESENTON_API_KEY" }, origin, allowed, 500);
  const presentationId = url.searchParams.get("id") || "";
  if (!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(presentationId)) {
    return json({ error: "Invalid presentation id" }, origin, allowed, 400);
  }

  // Presenton's editor blocks iframe embedding. Export the already-generated
  // deck as PDF and stream it from Atom so teachers can review it in place.
  const exportRes = await fetch(PRESENTON_API + "/presentation/export", {
    method: "POST",
    headers: { "Content-Type": "application/json", "Authorization": "Bearer " + env.PRESENTON_API_KEY },
    body: JSON.stringify({ id: presentationId, export_as: "pdf" }),
  });
  const exported = await exportRes.json();
  if (!exportRes.ok || !exported.path) {
    return json({ error: "Could not prepare presentation preview" }, origin, allowed, 502);
  }

  const pdfRes = await fetch(exported.path);
  if (!pdfRes.ok) return json({ error: "Could not load presentation preview" }, origin, allowed, 502);
  const headers = new Headers(corsHeaders(origin, allowed));
  headers.set("Content-Type", "application/pdf");
  headers.set("Content-Disposition", "inline; filename=atom-presentation.pdf");
  headers.set("Cache-Control", "private, no-store");
  return new Response(pdfRes.body, { status: 200, headers });
}

const GOOGLE_REDIRECT = "https://atom-edu.pritamavuthu7.workers.dev/api/google/callback";
const SITE_URL = "https://atom-edu.org";

async function handleGooglePrepare(request, env, origin, allowed) {
  if (!env.GOOGLE_CLIENT_ID) return json({ error: "Server missing GOOGLE_CLIENT_ID" }, origin, allowed, 500);
  if (!env.RATE_KV) return json({ error: "KV not bound" }, origin, allowed, 500);
  const body = await request.json();
  const content = (body.content || "").toString();
  if (!content.trim()) return json({ error: "content required" }, origin, allowed, 400);
  const title = (body.title || "Slides from Atom Edu").toString().slice(0, 120);

  const sid = crypto.randomUUID().replace(/-/g, "");
  await env.RATE_KV.put("gsld:" + sid, JSON.stringify({ content: content.slice(0, 16000), title }), { expirationTtl: 600 });

  const p = new URLSearchParams({
    client_id: env.GOOGLE_CLIENT_ID,
    redirect_uri: GOOGLE_REDIRECT,
    response_type: "code",
    scope: "https://www.googleapis.com/auth/drive.file openid https://www.googleapis.com/auth/userinfo.email",
    access_type: "online",
    include_granted_scopes: "true",
    prompt: "consent",
    state: sid,
  });
  return json({ authUrl: "https://accounts.google.com/o/oauth2/v2/auth?" + p.toString() }, origin, allowed);
}

function redirectTo(u) {
  return new Response(null, { status: 302, headers: { Location: u } });
}

async function gErr(env, step, status, detail) {
  try {
    if (env.RATE_KV) await env.RATE_KV.put("gslerr:last", JSON.stringify({ step: step, status: status, detail: String(detail || "").slice(0, 900), ts: Date.now() }), { expirationTtl: 3600 });
  } catch (e) {}
  return redirectTo(SITE_URL + "/?gslides=error&why=" + encodeURIComponent(step));
}

async function handleGoogleDebug(request, env, url, origin, allowed) {
  const t = url.searchParams.get("t") || "";
  if (!env.GOOGLE_DEBUG_TOKEN || t !== env.GOOGLE_DEBUG_TOKEN) return json({ error: "forbidden" }, origin, allowed, 403);
  if (!env.RATE_KV) return json({ error: "no kv" }, origin, allowed, 500);
  const raw = await env.RATE_KV.get("gslerr:last");
  return json({ lastError: raw ? JSON.parse(raw) : null }, origin, allowed);
}

async function handleGoogleCallback(request, env, url) {
  const err = url.searchParams.get("error");
  if (err) return redirectTo(SITE_URL + "/?gslides=denied");
  const code = url.searchParams.get("code");
  const sid = url.searchParams.get("state");
  if (!code || !sid) return await gErr(env, "params", 0, "missing code or state");
  if (!env.GOOGLE_CLIENT_ID || !env.GOOGLE_CLIENT_SECRET || !env.RATE_KV) {
    return await gErr(env, "config", 0, "id=" + !!env.GOOGLE_CLIENT_ID + " secret=" + !!env.GOOGLE_CLIENT_SECRET + " kv=" + !!env.RATE_KV);
  }

  try {
    const tokRes = await fetch("https://oauth2.googleapis.com/token", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: new URLSearchParams({
        code: code,
        client_id: env.GOOGLE_CLIENT_ID,
        client_secret: env.GOOGLE_CLIENT_SECRET,
        redirect_uri: GOOGLE_REDIRECT,
        grant_type: "authorization_code",
      }).toString(),
    });
    const tok = await tokRes.json();
    if (!tokRes.ok || !tok.access_token) return await gErr(env, "token", tokRes.status, JSON.stringify(tok));
    const token = tok.access_token;

    const raw = await env.RATE_KV.get("gsld:" + sid);
    if (!raw) return redirectTo(SITE_URL + "/?gslides=expired");
    await env.RATE_KV.delete("gsld:" + sid);
    const parsedRaw = JSON.parse(raw);
    const parsed = parseSlides(parsedRaw.content, parsedRaw.title);

    const createRes = await fetch("https://slides.googleapis.com/v1/presentations", {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: "Bearer " + token },
      body: JSON.stringify({ title: parsed.title }),
    });
    const pres = await createRes.json();
    if (!createRes.ok || !pres.presentationId) return await gErr(env, "create", createRes.status, JSON.stringify(pres));
    const pid = pres.presentationId;
    const defaultSlideId = (pres.slides && pres.slides[0] && pres.slides[0].objectId) || null;

    const requests = [];
    parsed.slides.forEach(function (sl, idx) {
      const s2 = "slide_" + idx;
      requests.push({
        createSlide: {
          objectId: s2,
          slideLayoutReference: { predefinedLayout: "TITLE_AND_BODY" },
          placeholderIdMappings: [
            { layoutPlaceholder: { type: "TITLE", index: 0 }, objectId: s2 + "_t" },
            { layoutPlaceholder: { type: "BODY", index: 0 }, objectId: s2 + "_b" },
          ],
        },
      });
      if (sl.title) requests.push({ insertText: { objectId: s2 + "_t", text: sl.title } });
      if (sl.body) requests.push({ insertText: { objectId: s2 + "_b", text: sl.body } });
    });
    if (defaultSlideId) requests.push({ deleteObject: { objectId: defaultSlideId } });

    if (requests.length) {
      const buRes = await fetch("https://slides.googleapis.com/v1/presentations/" + pid + ":batchUpdate", {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: "Bearer " + token },
        body: JSON.stringify({ requests: requests }),
      });
      if (!buRes.ok) {
        const bu = await buRes.json().catch(function () { return {}; });
        await gErr(env, "batch", buRes.status, JSON.stringify(bu));
      }
    }

    return redirectTo("https://docs.google.com/presentation/d/" + pid + "/edit");
  } catch (e) {
    return await gErr(env, "exception", 0, e && e.message ? e.message : String(e));
  }
}

function parseSlides(content, fallbackTitle) {
  const lines = content.replace(/\r/g, "").split("\n");
  let deckTitle = fallbackTitle || "Slides";
  let started = false;
  const slides = [];
  let cur = null;
  let skipRest = false;
  const slideRe = /^\s*slide\s*\d+\s*[:\-\.]\s*(.+)$/i;

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmed = line.trim();
    const m = trimmed.match(slideRe);
    if (m) {
      cur = { title: m[1].trim(), bodyLines: [] };
      slides.push(cur);
      skipRest = false;
      started = true;
      continue;
    }
    if (!started) {
      // first non-empty line before any "Slide N:" is the deck title
      if (trimmed && deckTitle === (fallbackTitle || "Slides")) { deckTitle = trimmed.slice(0, 120); }
      continue;
    }
    if (!cur) continue;
    if (/^\s*speaker notes\s*:?/i.test(trimmed)) { skipRest = true; continue; }
    if (skipRest) continue;
    if (!trimmed) { cur.bodyLines.push(""); continue; }
    const clean = trimmed.replace(/^[-*\u2022]\s*/, "");
    cur.bodyLines.push(clean);
  }

  // Fallback: no "Slide N:" markers found, make one slide from the whole thing
  if (!slides.length) {
    const nonEmpty = lines.map(function (l) { return l.trim(); }).filter(Boolean);
    deckTitle = nonEmpty[0] ? nonEmpty[0].slice(0, 120) : deckTitle;
    slides.push({ title: deckTitle, bodyLines: nonEmpty.slice(1) });
  }

  const out = slides.map(function (s) {
    let body = s.bodyLines.join("\n").replace(/\n{3,}/g, "\n\n").trim();
    if (body.length > 1800) body = body.slice(0, 1800);
    return { title: (s.title || "").slice(0, 200), body };
  });
  return { title: deckTitle, slides: out };
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
  if (!(await passwordsMatch(password, env.ADMIN_PASSWORD))) {
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

async function handleAdminDeleteUser(request, env, origin, allowed) {
  const { password, email, confirmation } = await request.json();
  if (!env.ADMIN_PASSWORD) return json({ error: "Server missing ADMIN_PASSWORD" }, origin, allowed, 500);
  if (!(await passwordsMatch(password, env.ADMIN_PASSWORD))) {
    return json({ error: "Wrong password" }, origin, allowed, 401);
  }
  if (!env.RATE_KV) return json({ error: "KV not bound" }, origin, allowed, 500);

  const normalizedEmail = String(email || "").trim().toLowerCase();
  if (!/^[a-z0-9._%+\-]+@[a-z0-9.\-]+\.(edu|org)$/.test(normalizedEmail)) {
    return json({ error: "Enter a valid .edu or .org email address" }, origin, allowed, 400);
  }
  if (confirmation !== "DELETE") {
    return json({ error: "Confirmation must be DELETE" }, origin, allowed, 400);
  }

  const kv = env.RATE_KV;
  const emails = JSON.parse((await kv.get("stat:emails")) || "[]");
  const nextEmails = emails.filter((storedEmail) => storedEmail !== normalizedEmail);
  const recent = JSON.parse((await kv.get("stat:recent")) || "[]");
  const nextRecent = recent.filter((activity) => activity.email !== normalizedEmail);
  const rateLimitKeys = await listKeys(kv, "rl:" + normalizedEmail + ":");

  await Promise.all([
    kv.delete("stat:email:" + normalizedEmail),
    kv.put("stat:emails", JSON.stringify(nextEmails)),
    kv.put("stat:recent", JSON.stringify(nextRecent)),
    ...rateLimitKeys.map((key) => kv.delete(key)),
  ]);

  return json({ ok: true, deleted: normalizedEmail }, origin, allowed);
}

async function passwordsMatch(provided, expected) {
  if (typeof provided !== "string" || typeof expected !== "string") return false;
  const encoder = new TextEncoder();
  const a = encoder.encode(provided);
  const b = encoder.encode(expected);
  if (a.length !== b.length) return false;
  return crypto.subtle.timingSafeEqual(a, b);
}

async function listKeys(kv, prefix) {
  const keys = [];
  let cursor;
  for (;;) {
    const result = await kv.list({ prefix, cursor });
    keys.push(...result.keys.map((key) => key.name));
    if (result.list_complete) return keys;
    cursor = result.cursor;
  }
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

// ===================== LTI 1.3 (Advantage) =====================
// Atom Edu as a certified-grade LTI 1.3 tool.
//   GET/POST /lti/login     OIDC third-party login initiation
//   POST     /lti/launch    Launch (validates id_token) + Deep Linking response
//   GET      /lti/jwks      Tool public JWKS (RSA key auto-generated in KV)
//   POST     /lti/session   Exchange one-time launch ticket for session (no PII in URL)
//   GET/POST /lti/register  Dynamic Registration (1EdTech) for one-click install
//   GET      /lti/config    Canvas LTI JSON config (manual install)
// No new secrets required. Tool RSA key + platform registrations live in KV.

const LTI = {
  tool_title: "Atom Edu",
  tool_desc: "Free AI workbench for teachers: assignments, quizzes, rubrics, lessons, slides, translations.",
};

function ltiUrls(env) {
  const base = (env.WORKER_URL || "https://atom-edu.pritamavuthu7.workers.dev").replace(/\/+$/, "");
  const site = (env.SITE_URL || "https://atom-edu.org").replace(/\/+$/, "");
  return { base, site, login: base + "/lti/login", launch: base + "/lti/launch", jwks: base + "/lti/jwks", register: base + "/lti/register" };
}

// Known Canvas platform endpoints so a manual Developer Key install works with
// no Dynamic Registration round-trip.
function canvasDefaults(issuer) {
  const iss = (issuer || "").replace(/\/+$/, "");
  const hosts = {
    "https://canvas.instructure.com": "https://sso.canvaslms.com",
    "https://canvas.beta.instructure.com": "https://sso.beta.canvaslms.com",
    "https://canvas.test.instructure.com": "https://sso.test.canvaslms.com",
  };
  const sso = hosts[iss];
  if (!sso) return null;
  return {
    issuer: iss,
    authorization_endpoint: sso + "/api/lti/authorize_redirect",
    jwks_uri: sso + "/api/lti/security/jwks",
    token_endpoint: sso + "/login/oauth2/token",
  };
}

// ---- Tool key (RSA, RS256) -------------------------------------------------
async function getToolKey(env) {
  if (!env.RATE_KV) throw new Error("KV not bound");
  const raw = await env.RATE_KV.get("lti:key");
  if (raw) return JSON.parse(raw);
  const pair = await crypto.subtle.generateKey(
    { name: "RSASSA-PKCS1-v1_5", modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: "SHA-256" },
    true, ["sign", "verify"]
  );
  const priv = await crypto.subtle.exportKey("jwk", pair.privateKey);
  const pub = await crypto.subtle.exportKey("jwk", pair.publicKey);
  const kid = "atom-" + hex(crypto.getRandomValues(new Uint8Array(8)));
  priv.kid = kid; priv.alg = "RS256"; priv.use = "sig";
  pub.kid = kid; pub.alg = "RS256"; pub.use = "sig";
  const rec = { kid, priv, pub };
  await env.RATE_KV.put("lti:key", JSON.stringify(rec));
  return rec;
}
async function toolSignKey(env) {
  const rec = await getToolKey(env);
  const key = await crypto.subtle.importKey("jwk", rec.priv, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["sign"]);
  return { key, kid: rec.kid };
}
async function handleLtiJwks(env, origin, allowed) {
  const rec = await getToolKey(env);
  return json({ keys: [rec.pub] }, origin, allowed);
}

// ---- base64url + hex helpers ----------------------------------------------
function hex(bytes) { let s = ""; for (let i = 0; i < bytes.length; i++) s += bytes[i].toString(16).padStart(2, "0"); return s; }
function b64urlFromBytes(bytes) { let s = ""; for (let i = 0; i < bytes.length; i++) s += String.fromCharCode(bytes[i]); return btoa(s).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, ""); }
function b64urlToBytes(b) { let s = b.replace(/-/g, "+").replace(/_/g, "/"); while (s.length % 4) s += "="; const bin = atob(s); const a = new Uint8Array(bin.length); for (let i = 0; i < bin.length; i++) a[i] = bin.charCodeAt(i); return a; }
function b64urlEncodeStr(str) { return b64urlFromBytes(new TextEncoder().encode(str)); }
function b64urlDecodeStr(b) { return new TextDecoder().decode(b64urlToBytes(b)); }

// ---- JWT sign / verify -----------------------------------------------------
async function signJwt(env, payload, extraHeader) {
  const { key, kid } = await toolSignKey(env);
  const header = Object.assign({ alg: "RS256", typ: "JWT", kid }, extraHeader || {});
  const h = b64urlEncodeStr(JSON.stringify(header));
  const p = b64urlEncodeStr(JSON.stringify(payload));
  const data = new TextEncoder().encode(h + "." + p);
  const sig = await crypto.subtle.sign({ name: "RSASSA-PKCS1-v1_5" }, key, data);
  return h + "." + p + "." + b64urlFromBytes(new Uint8Array(sig));
}
async function verifyToolJwt(env, token) {
  try {
    const rec = await getToolKey(env);
    const parts = String(token).split(".");
    if (parts.length !== 3) return null;
    const key = await crypto.subtle.importKey("jwk", rec.pub, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
    const data = new TextEncoder().encode(parts[0] + "." + parts[1]);
    const ok = await crypto.subtle.verify({ name: "RSASSA-PKCS1-v1_5" }, key, b64urlToBytes(parts[2]), data);
    if (!ok) return null;
    const payload = JSON.parse(b64urlDecodeStr(parts[1]));
    if (payload.exp && Date.now() / 1000 > payload.exp) return null;
    return payload;
  } catch (e) { return null; }
}
function decodeJwtParts(token) {
  const parts = String(token).split(".");
  if (parts.length !== 3) return null;
  try {
    return {
      header: JSON.parse(b64urlDecodeStr(parts[0])),
      payload: JSON.parse(b64urlDecodeStr(parts[1])),
      signingInput: parts[0] + "." + parts[1],
      sig: b64urlToBytes(parts[2]),
    };
  } catch (e) { return null; }
}
async function fetchJwksCached(jwksUri, env) {
  const ck = "lti:pjwks:" + jwksUri;
  if (env.RATE_KV) {
    const cached = await env.RATE_KV.get(ck);
    if (cached) { try { return JSON.parse(cached); } catch (e) {} }
  }
  const res = await fetch(jwksUri, { headers: { Accept: "application/json" } });
  if (!res.ok) return null;
  const data = await res.json();
  if (env.RATE_KV) await env.RATE_KV.put(ck, JSON.stringify(data), { expirationTtl: 3600 });
  return data;
}
async function verifyPlatformJwt(token, jwksUri, env) {
  const dec = decodeJwtParts(token);
  if (!dec) return { ok: false, error: "malformed id_token" };
  const jwks = await fetchJwksCached(jwksUri, env);
  if (!jwks || !jwks.keys) return { ok: false, error: "cannot fetch platform jwks" };
  const jwk = jwks.keys.find((k) => k.kid === dec.header.kid) || (jwks.keys.length === 1 ? jwks.keys[0] : null);
  if (!jwk) return { ok: false, error: "no matching platform key" };
  const key = await crypto.subtle.importKey("jwk", { kty: jwk.kty, n: jwk.n, e: jwk.e, alg: "RS256", ext: true }, { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" }, false, ["verify"]);
  const ok = await crypto.subtle.verify({ name: "RSASSA-PKCS1-v1_5" }, key, dec.sig, new TextEncoder().encode(dec.signingInput));
  if (!ok) return { ok: false, error: "bad id_token signature" };
  return { ok: true, payload: dec.payload };
}

// ---- Platform registration store ------------------------------------------
async function getRegistration(env, issuer, clientId) {
  if (env.RATE_KV) {
    const raw = await env.RATE_KV.get("lti:reg:" + issuer);
    if (raw) {
      try {
        const map = JSON.parse(raw);
        if (clientId && map[clientId]) return map[clientId];
        const keys = Object.keys(map);
        if (!clientId && keys.length === 1) return map[keys[0]];
      } catch (e) {}
    }
  }
  const def = canvasDefaults(issuer);
  if (def && clientId) {
    return { issuer, client_id: clientId, authorization_endpoint: def.authorization_endpoint, jwks_uri: def.jwks_uri, token_endpoint: def.token_endpoint };
  }
  return null;
}
async function saveRegistration(env, reg) {
  if (!env.RATE_KV) return;
  const raw = await env.RATE_KV.get("lti:reg:" + reg.issuer);
  let map = {};
  if (raw) { try { map = JSON.parse(raw); } catch (e) {} }
  map[reg.client_id] = reg;
  await env.RATE_KV.put("lti:reg:" + reg.issuer, JSON.stringify(map));
}

// ---- OIDC login initiation -------------------------------------------------
async function readParams(request, url) {
  if (request.method === "POST") {
    const ct = request.headers.get("Content-Type") || "";
    if (ct.includes("application/json")) {
      const b = await request.json().catch(() => ({}));
      return new URLSearchParams(Object.entries(b).map(([k, v]) => [k, String(v)]));
    }
    const form = await request.formData().catch(() => null);
    const p = new URLSearchParams();
    if (form) for (const [k, v] of form) p.set(k, String(v));
    return p;
  }
  return url.searchParams;
}
async function handleLtiLogin(request, env, url) {
  const params = await readParams(request, url);
  const issuer = (params.get("iss") || "").replace(/\/+$/, "");
  const loginHint = params.get("login_hint") || "";
  const targetLinkUri = params.get("target_link_uri") || ltiUrls(env).launch;
  const ltiMessageHint = params.get("lti_message_hint") || "";
  const clientId = params.get("client_id") || "";
  const deploymentId = params.get("lti_deployment_id") || params.get("deployment_id") || "";
  if (!issuer) return htmlErr("Missing issuer (iss).", 400);
  const reg = await getRegistration(env, issuer, clientId);
  if (!reg) return htmlErr("This platform (" + esc(issuer) + ") is not registered with Atom Edu. Install via Dynamic Registration, or add a Developer Key and relaunch.", 400);
  const state = "st_" + hex(crypto.getRandomValues(new Uint8Array(16)));
  const nonce = "no_" + hex(crypto.getRandomValues(new Uint8Array(16)));
  if (env.RATE_KV) {
    await env.RATE_KV.put("lti:state:" + state, JSON.stringify({ nonce, issuer, client_id: reg.client_id, deployment_id: deploymentId, target_link_uri: targetLinkUri, ts: Date.now() }), { expirationTtl: 600 });
  }
  const auth = new URLSearchParams({
    scope: "openid", response_type: "id_token", response_mode: "form_post", prompt: "none",
    client_id: reg.client_id, redirect_uri: ltiUrls(env).launch, login_hint: loginHint, state, nonce,
  });
  if (ltiMessageHint) auth.set("lti_message_hint", ltiMessageHint);
  return redirectTo(reg.authorization_endpoint + "?" + auth.toString());
}

// ---- Launch (resource link + deep linking) --------------------------------
async function handleLtiLaunch(request, env, url) {
  const ct = request.headers.get("Content-Type") || "";
  let idToken = "", state = "";
  if (ct.includes("application/x-www-form-urlencoded") || ct.includes("multipart/form-data")) {
    const form = await request.formData();
    idToken = form.get("id_token") || "";
    state = form.get("state") || "";
  } else {
    idToken = url.searchParams.get("id_token") || "";
    state = url.searchParams.get("state") || "";
  }
  if (!idToken || !state) return htmlErr("Missing id_token or state.", 400);

  let st = null;
  if (env.RATE_KV) {
    const raw = await env.RATE_KV.get("lti:state:" + state);
    if (raw) { try { st = JSON.parse(raw); } catch (e) {} await env.RATE_KV.delete("lti:state:" + state); }
  }
  if (!st) return htmlErr("Invalid or expired launch (state). Please relaunch from your LMS.", 400);

  const reg = await getRegistration(env, st.issuer, st.client_id);
  if (!reg) return htmlErr("Platform not registered.", 400);

  const v = await verifyPlatformJwt(idToken, reg.jwks_uri, env);
  if (!v.ok) return htmlErr("Launch verification failed: " + esc(v.error), 401);
  const p = v.payload;

  const now = Math.floor(Date.now() / 1000);
  if (p.iss !== st.issuer) return htmlErr("Issuer mismatch.", 401);
  const aud = Array.isArray(p.aud) ? p.aud : [p.aud];
  if (!aud.includes(reg.client_id)) return htmlErr("Audience mismatch.", 401);
  if (Array.isArray(p.aud) && p.aud.length > 1 && p.azp && p.azp !== reg.client_id) return htmlErr("azp mismatch.", 401);
  if (typeof p.exp === "number" && now > p.exp + 60) return htmlErr("id_token expired.", 401);
  if (typeof p.iat === "number" && p.iat > now + 300) return htmlErr("id_token issued in the future.", 401);
  if (!p.nonce || p.nonce !== st.nonce) return htmlErr("Nonce mismatch.", 401);
  if (env.RATE_KV) {
    const nk = "lti:nonce:" + p.nonce;
    if (await env.RATE_KV.get(nk)) return htmlErr("Replay detected (nonce reused).", 401);
    await env.RATE_KV.put(nk, "1", { expirationTtl: 600 });
  }

  const C = "https://purl.imsglobal.org/spec/lti/claim/";
  const msgType = p[C + "message_type"];
  const version = p[C + "version"] || "1.3.0";
  if (String(version).indexOf("1.3") !== 0) return htmlErr("Unsupported LTI version.", 401);
  const deploymentId = p[C + "deployment_id"] || st.deployment_id || "";
  if (deploymentId && (!reg.deployment_ids || reg.deployment_ids.indexOf(deploymentId) < 0)) {
    reg.deployment_ids = (reg.deployment_ids || []).concat([deploymentId]);
    await saveRegistration(env, reg);
  }

  if (msgType === "LtiDeepLinkingRequest") {
    return await ltiDeepLinkResponse(env, p, reg, deploymentId);
  }

  const custom = p[C + "custom"] || {};
  const name = p.name || [p.given_name, p.family_name].filter(Boolean).join(" ").trim() || custom.person_name_full || "Teacher";
  const email = p.email || custom.person_email || "";
  const ctx = p[C + "context"] || {};
  const contextTitle = ctx.title || custom.context_title || "My class";
  const roles = p[C + "roles"] || [];

  const session = await signJwt(env, {
    iss: "atom-edu", sub: (email || "lti:" + (p.sub || "user")).toLowerCase(),
    name, email, ctx: contextTitle, lti: true, iat: now, exp: now + 60 * 60 * 12,
  });

  // Keep PII out of the URL: stash launch data, hand the SPA a one-time ticket.
  const ticket = "tk_" + hex(crypto.getRandomValues(new Uint8Array(16)));
  if (env.RATE_KV) {
    await env.RATE_KV.put("lti:tkt:" + ticket, JSON.stringify({ name, email, ctx: contextTitle, session, roles }), { expirationTtl: 120 });
  }
  return redirectTo(ltiUrls(env).site + "/?lti=" + ticket);
}

async function handleLtiSession(request, env, origin, allowed) {
  const body = await request.json().catch(() => ({}));
  const ticket = (body.ticket || "").toString();
  if (!ticket || !env.RATE_KV) return json({ error: "invalid ticket" }, origin, allowed, 400);
  const raw = await env.RATE_KV.get("lti:tkt:" + ticket);
  if (!raw) return json({ error: "expired" }, origin, allowed, 400);
  await env.RATE_KV.delete("lti:tkt:" + ticket);
  return json(JSON.parse(raw), origin, allowed);
}

async function ltiDeepLinkResponse(env, p, reg, deploymentId) {
  const DL = "https://purl.imsglobal.org/spec/lti-dl/claim/";
  const C = "https://purl.imsglobal.org/spec/lti/claim/";
  const settings = p[DL + "deep_linking_settings"] || {};
  const returnUrl = settings.deep_link_return_url;
  if (!returnUrl) return htmlErr("No deep_link_return_url in request.", 400);
  const now = Math.floor(Date.now() / 1000);
  const contentItems = [{
    type: "ltiResourceLink",
    title: "Atom Edu",
    text: "Open Atom Edu to draft assignments, quizzes, rubrics, lessons, and slides.",
    url: ltiUrls(env).launch,
    presentation: { documentTarget: "window" },
  }];
  const payload = {
    iss: reg.client_id, aud: reg.issuer, iat: now, exp: now + 600,
    nonce: "dl_" + hex(crypto.getRandomValues(new Uint8Array(12))),
    [C + "message_type"]: "LtiDeepLinkingResponse",
    [C + "version"]: "1.3.0",
    [C + "deployment_id"]: deploymentId,
    [DL + "content_items"]: contentItems,
  };
  if (settings.data) payload[DL + "data"] = settings.data;
  const jwt = await signJwt(env, payload);
  const html = "<!doctype html><html><body onload=\"document.forms[0].submit()\">" +
    "<form method=\"POST\" action=\"" + esc(returnUrl) + "\">" +
    "<input type=\"hidden\" name=\"JWT\" value=\"" + esc(jwt) + "\"/>" +
    "</form><noscript><button type=\"submit\">Return to your course</button></noscript>" +
    "</body></html>";
  return new Response(html, { status: 200, headers: { "Content-Type": "text/html; charset=utf-8" } });
}

// ---- Dynamic Registration (1EdTech) ---------------------------------------
async function handleLtiRegister(request, env, url) {
  const openidConfigUrl = url.searchParams.get("openid_configuration");
  const regToken = url.searchParams.get("registration_token") || "";
  const u = ltiUrls(env);
  if (!openidConfigUrl) {
    return htmlPage("Atom Edu — LTI 1.3", "<p>This is the Atom Edu Dynamic Registration endpoint. In your LMS, paste this URL into the LTI 1.3 Dynamic Registration field:</p><p><code>" + esc(u.register) + "</code></p><p>Canvas: Admin &rsaquo; Developer Keys &rsaquo; + LTI Registration &rsaquo; enter this URL.</p>");
  }
  const cfgRes = await fetch(openidConfigUrl, { headers: { Accept: "application/json" } });
  if (!cfgRes.ok) return htmlErr("Could not fetch platform OpenID configuration.", 400);
  const cfg = await cfgRes.json();
  const host = new URL(u.site).host;
  const canvasExt = "https://canvas.instructure.com/lti";
  const toolReg = {
    application_type: "web",
    response_types: ["id_token"],
    grant_types: ["client_credentials", "implicit"],
    initiate_login_uri: u.login,
    redirect_uris: [u.launch],
    client_name: LTI.tool_title,
    jwks_uri: u.jwks,
    logo_uri: u.site + "/favicon.png",
    token_endpoint_auth_method: "private_key_jwt",
    scope: [
      "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
      "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
      "https://purl.imsglobal.org/spec/lti-ags/scope/score",
      "https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly",
    ].join(" "),
    "https://purl.imsglobal.org/spec/lti-tool-configuration": {
      domain: host,
      target_link_uri: u.launch,
      claims: ["iss", "sub", "name", "given_name", "family_name", "email"],
      description: LTI.tool_desc,
      messages: [
        { type: "LtiResourceLinkRequest", target_link_uri: u.launch, label: "Atom Edu", placements: ["course_navigation"], [canvasExt + "/course_navigation/default_enabled"]: true, "https://purl.imsglobal.org/spec/lti/claim/launch_presentation": { document_target: "window" } },
        { type: "LtiDeepLinkingRequest", target_link_uri: u.launch, label: "Add Atom Edu", placements: ["link_selection", "assignment_selection"] },
      ],
      custom_parameters: { person_email: "$Person.email.primary", person_name_full: "$Person.name.full", context_title: "$Context.title" },
    },
  };
  const regEndpoint = cfg.registration_endpoint;
  if (!regEndpoint) return htmlErr("Platform has no registration_endpoint.", 400);
  const headers = { "Content-Type": "application/json", Accept: "application/json" };
  if (regToken) headers["Authorization"] = "Bearer " + regToken;
  const regRes = await fetch(regEndpoint, { method: "POST", headers, body: JSON.stringify(toolReg) });
  const regBody = await regRes.json().catch(() => ({}));
  if (!regRes.ok) return htmlErr("Registration failed: " + esc(JSON.stringify(regBody).slice(0, 400)), 400);
  const issuer = (cfg.issuer || "").replace(/\/+$/, "");
  const stored = {
    issuer, client_id: regBody.client_id,
    authorization_endpoint: cfg.authorization_endpoint,
    jwks_uri: cfg.jwks_uri,
    token_endpoint: cfg.token_endpoint,
    registered_at: Date.now(),
  };
  await saveRegistration(env, stored);
  const html = "<!doctype html><html><body style=\"font-family:system-ui;max-width:640px;margin:60px auto;padding:0 20px;color:#0b1226\">" +
    "<h2>Atom Edu is registered</h2><p>Registration succeeded. Close this window, then enable Atom Edu in your course placements.</p>" +
    "<script>if(window.opener){window.opener.postMessage({subject:'org.imsglobal.lti.close'},'*');}else if(window.parent!==window){window.parent.postMessage({subject:'org.imsglobal.lti.close'},'*');}</script>" +
    "</body></html>";
  return new Response(html, { status: 200, headers: { "Content-Type": "text/html; charset=utf-8" } });
}

// ---- Canvas manual config JSON --------------------------------------------
function handleLtiConfig(env, url) {
  const u = ltiUrls(env);
  const host = new URL(u.site).host;
  const cfg = {
    title: LTI.tool_title,
    description: LTI.tool_desc,
    oidc_initiation_url: u.login,
    target_link_uri: u.launch,
    public_jwk_url: u.jwks,
    scopes: [
      "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
      "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
      "https://purl.imsglobal.org/spec/lti-ags/scope/score",
      "https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly",
    ],
    extensions: [{
      domain: host,
      platform: "canvas.instructure.com",
      privacy_level: "public",
      settings: {
        text: "Atom Edu",
        icon_url: u.site + "/favicon.png",
        placements: [
          { placement: "course_navigation", message_type: "LtiResourceLinkRequest", target_link_uri: u.launch, text: "Atom Edu", windowTarget: "_blank", default: "enabled", enabled: true },
          { placement: "link_selection", message_type: "LtiDeepLinkingRequest", target_link_uri: u.launch, text: "Atom Edu", enabled: true },
          { placement: "assignment_selection", message_type: "LtiDeepLinkingRequest", target_link_uri: u.launch, text: "Atom Edu", enabled: true },
        ],
      },
    }],
    custom_fields: { person_email: "$Person.email.primary", person_name_full: "$Person.name.full", context_title: "$Context.title" },
  };
  return new Response(JSON.stringify(cfg, null, 2), { status: 200, headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" } });
}

// ---- tiny HTML helpers -----------------------------------------------------
function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;"); }
function htmlErr(msg, status) {
  return new Response("<!doctype html><meta charset=utf-8><body style=\"font-family:system-ui;max-width:640px;margin:60px auto;padding:0 20px;color:#0b1226\"><h2>Atom Edu — LTI</h2><p>" + esc(msg) + "</p></body>", { status: status || 400, headers: { "Content-Type": "text/html; charset=utf-8" } });
}
function htmlPage(title, bodyHtml) {
  return new Response("<!doctype html><meta charset=utf-8><title>" + esc(title) + "</title><body style=\"font-family:system-ui;max-width:640px;margin:60px auto;padding:0 20px;color:#0b1226\"><h2>" + esc(title) + "</h2>" + bodyHtml + "</body>", { status: 200, headers: { "Content-Type": "text/html; charset=utf-8" } });
}
