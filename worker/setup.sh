#!/usr/bin/env bash
# Atom Edu — Cloudflare Worker setup.
# One-time: install wrangler, log in, set both secrets, deploy.
set -euo pipefail

# 0. Install wrangler if you don't have it (npm required).
#    npm i -g wrangler

# 1. Log in to Cloudflare (opens a browser).
wrangler login

# 2. Set the Groq API key as a secret.
#    You'll be prompted to paste the value (gsk_...). It never lands on disk.
wrangler secret put GROQ_API_KEY

# 3. Generate a fresh 256-bit AES-GCM key (base64) and set it as a secret.
#    Copy the printed value, then paste when prompted.
ENC_KEY="$(openssl rand -base64 32)"
echo
echo "Generated ENCRYPTION_KEY (copy this exact string):"
echo "  $ENC_KEY"
echo
echo "$ENC_KEY" | wrangler secret put ENCRYPTION_KEY

# 4. (Optional) Create a KV namespace so the daily cap is enforced server-side
#    across sessions and devices, then paste the id into wrangler.toml.
# wrangler kv:namespace create RATE_KV

# 5. Deploy.
wrangler deploy

# 6. Verify the secrets are attached (values are never shown).
wrangler secret list

echo
echo "Done. Point the frontend at your Worker URL:"
echo "  window.ATOM_WORKER_URL = 'https://atom-edu.<your-subdomain>.workers.dev'"
