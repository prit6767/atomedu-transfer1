# Atom Edu — LTI 1.3 (Canvas / any LMS)

Atom Edu is an LTI 1.3 / LTI Advantage tool. It launches from any LMS that
speaks LTI 1.3 (Canvas, Schoology, Moodle, D2L Brightspace, Blackboard).
The teacher lands in Atom Edu already signed in — no separate account.

## Endpoints (Cloudflare Worker)

| Purpose                    | URL |
|----------------------------|-----|
| OIDC login initiation      | `https://atom-edu.pritamavuthu7.workers.dev/lti/login` |
| Redirect / target link URI | `https://atom-edu.pritamavuthu7.workers.dev/lti/launch` |
| Public JWKS                | `https://atom-edu.pritamavuthu7.workers.dev/lti/jwks` |
| Dynamic Registration       | `https://atom-edu.pritamavuthu7.workers.dev/lti/register` |
| Canvas JSON config         | `https://atom-edu.pritamavuthu7.workers.dev/lti/config` |

The tool signs with an RSA key generated on first use and stored in KV; the
public half is served at `/lti/jwks`. No secrets to manage for LTI.

## Install in Canvas — Option A: Dynamic Registration (fastest)

1. Admin ▸ **Developer Keys** ▸ **+ Developer Key** ▸ **+ LTI Registration**.
2. Paste the **Dynamic Registration** URL above, click **Continue**.
3. Confirm the placements, **Enable**.
4. Copy the resulting **Client ID**. In the course/account, Settings ▸ Apps ▸
   **+ App** ▸ *By Client ID*, paste it, **Submit**.

## Install in Canvas — Option B: Manual JSON

1. Admin ▸ **Developer Keys** ▸ **+ Developer Key** ▸ **+ LTI Key**.
2. Method: **Enter URL**, paste the **Canvas JSON config** URL above.
3. Redirect URI: the **/lti/launch** URL. Save, toggle the key **ON**.
4. Copy the **Client ID**, add the app *By Client ID* as in Option A.

Atom Edu opens from **Course Navigation** (new tab) and is available as a
**Deep Linking** item under assignment/link selection.

## Privacy

Privacy level is `public` so Atom Edu receives the teacher's name, email, and
course title to personalize the workspace. Nothing is stored server-side beyond
anonymous usage counts; drafts live in the teacher's browser. Grade passback
(AGS) and roster (NRPS) scopes are declared for future use and are read-only.

## What makes this LTI 1.3 compliant

- OIDC third-party login with per-launch `state` + `nonce` (single-use).
- Full `id_token` validation: RS256 signature via the platform JWKS, and
  `iss` / `aud` / `azp` / `exp` / `iat` / `nonce` checks, plus replay protection.
- Tool JWKS endpoint with a stable RSA key.
- LTI Advantage: Deep Linking 2.0 response, AGS + NRPS scopes declared.
- 1EdTech Dynamic Registration for one-click install.
