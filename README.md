# LeLinc

Social media automation engine for Key View Digital. Single Docker container
per client: NGINX (dashboard/onboarding), Cloak Browser ([CloakHQ/CloakBrowser](https://github.com/CloakHQ/cloakbrowser)
- real stealth Chromium, source-level fingerprint patches, no VNC), Cookie
Grant Agent, QC Engine, Orchestrator.

See `ARCHITECTURE.md` for the full system design and `BUILD.md` for the build
spec this repo implements.

## Quick start

```bash
cp .env.example .env   # set HUNTER_API_KEY / HIBP_API_KEY if available
docker compose up --build
```

- `http://localhost/` — onboarding
- `http://localhost/dashboard?client_id=...` — client dashboard
- Cookie Grant API: `:8000`
- Orchestrator + QC API: `:8001`

## Status

Build order (per `BUILD.md`):

1. [x] docker-compose.yml + Dockerfile
2. [x] Cookie Grant Agent
3. [x] QC Engine
4. [x] Orchestrator (OSINT: Sherlock wired; Hunter.io/HIBP wired behind API keys)
5. [x] NGINX frontend (onboarding + dashboard)
6. [ ] Testing — full flow: onboarding → profiling → QC → report

The Cookie Grant browser extension (`extension/`) is now built and wired
into the dashboard - see `extension/README.md` for how it works and
`AGENTS.md` for why the login step needs it. Not yet published to the
Chrome Web Store; customers sideload it via `/extension-install.html`
during dev.

`cloak/entrypoint.sh` runs the real Cloak Browser binary (not a stock
Chromium placeholder) - `python -m cloakbrowser install` fetches it at
build time (free tier, no license key needed: Chromium v146, 58
source-level patches, unlimited sessions). Verified: image builds, binary
boots, CDP cookie injection (`Network.setCookies`) works against it.

**Business model note:** the free tier is what ships by default and is
what every client container runs - Garry isn't buying or reselling Cloak
Browser access; the product being sold is the aggregator (dashboard, QC,
orchestration) on top of it. `CLOAKBROWSER_LICENSE_KEY` is wired through
per-deployment (`.env`, per client) purely as an optional knob - if a
given client ever wants to supply their own Pro key for the newer
Chromium/more patches, that's their call and their cost, not something
baked into LeLinc's pricing.

Not yet built (KVD business layer, stubbed only): `pr_manager.py`,
`sales_manager.py`, `sales_agent.py`.

## Constraints

- Single container per client — no split services.
- No passwords stored — cookies only.
- One platform login at a time, never bulk.
- 2-of-3 rule for every claim shown to a client.
- Rate limit: 1 request / 3 sec / IP (enforced in `agents/rate_limit.py`).
- Cloak Browser only — no Playwright/Puppeteer, no VNC/noVNC anywhere.
