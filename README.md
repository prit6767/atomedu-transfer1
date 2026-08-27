# Atom Edu
Static site (`index.html`) + Cloudflare Worker (`worker/`) that proxies Groq and holds `GROQ_API_KEY` and `ENCRYPTION_KEY` as secrets.

## Deploy the worker
cd worker
npx wrangler login
npx wrangler secret put GROQ_API_KEY
openssl rand -base64 32 | npx wrangler secret put ENCRYPTION_KEY
npx wrangler deploy
