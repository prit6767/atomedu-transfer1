# Admin dashboard setup

The `admin/index.html` file gives you a password-gated analytics dashboard at `atom-edu.org/admin/`. It reads live data from your Cloudflare Worker.

## Steps (about 10 minutes)

### 1. Update the Worker

Replace the current `worker/src/worker.js` in your repo with the `worker.js` file in this zip.

```
cp worker.js ~/atomedu-fresh/worker/src/worker.js
```

### 2. Bind a KV namespace to your Worker

Analytics need a KV store. Create one, then wire it up in `wrangler.toml`.

```
cd ~/atomedu-fresh/worker
wrangler kv:namespace create RATE_KV
```

The output prints a namespace `id`. Copy it, then edit `wrangler.toml` and uncomment the KV block, pasting your id:

```
[[kv_namespaces]]
binding = "RATE_KV"
id = "PASTE_YOUR_NAMESPACE_ID_HERE"
```

### 3. Set the admin password

```
wrangler secret put ADMIN_PASSWORD
```

Type your admin password (something long, don't reuse it anywhere else), press enter.

### 4. Deploy the Worker

```
wrangler deploy
```

### 5. Add the admin page to the site

Copy the `admin` folder into your repo root:

```
cp -r admin ~/atomedu-fresh/admin
cd ~/atomedu-fresh
git add admin worker/src/worker.js worker/wrangler.toml
git commit -m "Add admin dashboard at /admin"
git push origin main
```

### 6. Visit atom-edu.org/admin

Wait 30 seconds for GitHub Pages to redeploy, then open [atom-edu.org/admin/](https://atom-edu.org/admin/) and enter your admin password.

## What the dashboard shows

- **Total drafts** all time
- **Drafts today** since midnight UTC
- **Teachers** (unique .edu / .org emails)
- **Error rate** today
- **Drafts this week** sparkline (Mon to Sun)
- **Model mix** which Groq models were used
- **Top domains** which schools use it most
- **Recent activity** last 10 drafts, emails redacted

## Privacy

- Emails are stored only for the "unique teacher" count and the "recent activity" feed.
- The activity feed shows the first two letters + the domain (e.g. `pr***@school.edu`).
- No prompts, no responses, no student data ever stored in the KV.
- Anyone with the admin password can see the dashboard. Rotate the password via `wrangler secret put ADMIN_PASSWORD` if it leaks.
