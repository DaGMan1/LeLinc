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

**Frontend redesign (2026-07-11):** onboarding and dashboard rebuilt with
a real design system (`nginx/styles.css` - shared tokens across all four
pages, both light/dark themes, teal accent distinct from generic AI-blue).
Dashboard no longer dumps raw JSON - `agents/orchestrator.py` now emits a
structured `findings` block (`build_findings()`) that the frontend renders
as honest, readable claims: only Sherlock is unconditionally wired, so
platform "signals" show 1/3 sources and are explicitly labeled as leads,
not verified claims, until Hunter/HIBP keys and more OSINT sources exist
to actually clear the 2-of-3 bar. Verified end to end via CDP device
emulation at a true 390px mobile viewport (light + dark) - not guessed;
an earlier round of screenshots via `chrome --window-size=390,844
--screenshot=` looked broken but turned out to be a Chrome headless "new"
mode quirk (enforces a ~500px minimum window, silently cropping the
image) rather than a real CSS bug - worth knowing if screenshotting this
app again, use CDP `Emulation.setDeviceMetricsOverride` instead of
`--window-size` for anything below ~500px.

**Connect flow rebuilt (2026-07-11):** the custom extension required
sideloading (zip, developer mode, load unpacked) - real friction for a
non-technical customer base, correctly called out as a blocker. Default
Connect flow is now `nginx/import-cookies.html`: open the real login page,
log in normally, export via the already-published, independent
["Get cookies.txt LOCALLY"](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
extension, drop the file on LeLinc. `POST /cookies/import`
(`agents/cookie_grant.py`) parses the Netscape cookie format (including
the `#HttpOnly_` prefix convention, since the actual session cookie is
httpOnly). Our own purpose-built extension (`extension/`) stays in the
repo as the future "fully automatic, no file" upgrade once it clears
Chrome Web Store review - not deleted, just not the default path anymore.

Two real bugs found and fixed while verifying this end to end (not
guessed - actually run through onboarding -> dashboard -> connect ->
findings with real data):
- `run_sherlock()` filtered on `line.startswith("http")`, but Sherlock's
  output format is `[+] SiteName: https://...` - that filter matched zero
  lines, ever. Sherlock has never returned a result in any test before
  this fix, regardless of whether a real profile existed.
- `RateLimitMiddleware` throttled every request per-IP, including GETs -
  a single dashboard page load fires two concurrent status fetches from
  the same IP, so one would 429 and render as "not connected"/"no
  profile found" even when the data was there. Now only mutating
  (non-GET) requests are throttled.

Also fixed: Sherlock was searching the literal business name ("Riverside
Cafe") as a username - real handles don't have spaces. `derive_usernames()`
now tries a slugified business name and the domain's root label instead.

Not yet built (KVD business layer, stubbed only): `pr_manager.py`,
`sales_manager.py`, `sales_agent.py`.

## Constraints

- Single container per client — no split services.
- No passwords stored — cookies only.
- One platform login at a time, never bulk.
- 2-of-3 rule for every claim shown to a client.
- Rate limit: 1 mutating request / 3 sec / IP (enforced in `agents/rate_limit.py`).
- Cloak Browser only — no Playwright/Puppeteer, no VNC/noVNC anywhere.
