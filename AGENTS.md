# AGENTS.md — Working Agreement for This Repo

> **Q, read this first:** business model correction, confirmed by Garry
> 2026-07-11 - free-tier Cloak Browser is the permanent setup, not a
> stopgap. Each client's container runs its own free Cloak Browser
> (unlimited sessions, no license). Garry isn't buying, reselling, or
> budgeting for Cloak Browser access at all - LeLinc's product is the
> aggregator (dashboard, QC, orchestration) on top of it, not Cloak
> Browser itself. If any spec doc frames Cloak Browser licensing/cost as
> something LeLinc needs to absorb or price around, that's wrong - fix it
> to match. Full detail in "Resolved: real Cloak Browser" further down
> this file. This note is also mirrored as `NOTE-FROM-CLAUDE-CODE.md` on
> `q-specs` in case that's the only branch you read.

This repo now has two branches:

- **`main`** — the implementation. Owned by this Claude Code instance,
  running in a sandboxed session Garry drives directly. This is where the
  actual buildable code lives.
- **`q-specs`** — architecture/spec docs, owned by Q via a Claude Code
  instance it directs on the VPS (`/home/claude-user/lelinc-repo/`,
  commits as `claude-code@lelinc.dev`).

## Why two branches (2026-07-11)

Q's instance pushed to `main` directly twice, twice force-pushing a
rewritten history that wiped the entire implementation down to just the
two spec docs. Nothing was lost either time (this session had the full
history locally and restored it), but repeated churn on a shared `main`
isn't sustainable. Splitting it: `q-specs` is Q's to push to freely,
however often, with no risk to the implementation. This session reads
`q-specs` and deliberately pulls in whatever's relevant to `main` -
spec updates don't auto-apply to the running code.

Note: a deploy key grants repo-wide access, not per-branch - this split
is a convention, not an enforced permission boundary. If Q's instance
keeps pushing to `main` instead of `q-specs`, the real fix is GitHub
branch protection on `main` (requires repo-admin access, which this
session doesn't have via its deploy key) - Garry, that'd need to come
from you via the GitHub web UI if the convention doesn't hold.

## Ownership

- **Q's instance** — architecture/spec docs. If a spec change affects the
  running code, note it in the Handoff Log below rather than editing
  implementation files directly; it'll get picked up and implemented
  deliberately.
- **This session** — the actual implementation: `agents/`, `cloak/`,
  `nginx/`, `Dockerfile`, `docker-compose.yml`, `start.sh`, `README.md`.
- **Non-negotiable:** no VNC/noVNC anywhere. Garry explicitly rejected
  noVNC/remote-desktop approaches for LeLinc's browser layer on the prior
  build ("it is slow it is clunky it does not work"). `BUILD.md` at one
  point re-added a noVNC port (6901) - that doesn't reflect Garry's
  decision and shouldn't ship.
- **API contract** — the endpoint paths currently implemented and tested
  in code (`agents/cookie_grant.py`, `agents/orchestrator.py`) are
  canonical: `GET /cookies/status/{client_id}`, `GET /onboard/status/{id}`,
  etc. If the spec proposes different paths, that's a proposal for the
  Handoff Log, not something to assume is already applied.

## Ground rules

1. **Don't force-push `main`.** Normal commits only.
2. **Pull before you push.**
3. **State the "why" in commit messages** - neither side has memory of
   the other's conversation, only git history and this file.
4. **`README.md`'s Status section is the single source of truth** for
   what's actually built and working (verified end to end, not just
   written) vs still pending.

## Resolved: Cookie Grant Flow mechanism (2026-07-11)

`ARCHITECTURE.md` §1a (from `q-specs`) described NGINX reverse-proxying
the real platform login page and Cookie Grant monitoring it via CDP. That
approach is **not being built** - flagged the reasoning below, Garry
confirmed the original 2026-07-09 decision instead:

- Reverse-proxying the login page doesn't change where the interaction
  happens if Cookie Grant still needs CDP visibility into that session -
  it's the same remote-relay input-timing problem that CAPTCHA-locked
  Instagram before, just with a proxy layer on top.
- It also puts NGINX in the path of the raw login POST, which cuts against
  "we never see the password" regardless of intent.

**What's actually built (`extension/`):** a Chrome extension (Manifest
V3, stable ID via a pinned `key` in `manifest.json`:
`jcidoldmjbfbbhnalodchgkcjbimkecf`). Dashboard button -> extension opens
the real login page in a normal tab (zero relay) -> client logs in exactly
as always -> extension detects the platform's session cookie landing ->
reads all cookies for that domain via the `cookies` API -> POSTs to
`POST /cookies` -> closes the tab. See `extension/README.md` for the full
flow. This is the only place a browser extension is involved - everything
after a platform is connected (dashboard, DMs, aggregation, automation)
runs entirely through Cloak Browser, same as the rest of this spec.

Not yet done: Chrome Web Store publishing (currently sideloaded via
`/extension-install.html`), Firefox/Safari support, real end-to-end test
against actual Instagram/LinkedIn/Facebook/TikTok logins (verified so far:
image builds, extension zip serves correctly, manifest/background.js are
syntactically valid - not yet tested against a live platform login, which
needs a real Chrome browser this sandbox doesn't have).

## Superseded: sideloaded extension is no longer the default Connect flow (2026-07-11)

Garry correctly called out that sideloading (zip → developer mode → load
unpacked) is real friction for a non-technical customer base - not an
acceptable default, whatever its technical merits. `extension/` and
`/extension-install.html` are **not deleted** - they're the future
"fully automatic, no file" path once published to the Chrome Web Store -
but the dashboard's Connect button no longer routes there.

**Default Connect flow is now `nginx/import-cookies.html`:** open the
real login page → log in normally → export cookies via the already-
published, independent ["Get cookies.txt LOCALLY"](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc)
extension (zero review wait, since we don't own or publish it) → drop the
file on LeLinc. New `POST /cookies/import` in `agents/cookie_grant.py`
parses the Netscape cookie file format, including the `#HttpOnly_` prefix
convention most exporters use to mark httpOnly cookies (which is exactly
the class of cookie a session token is). Verified end to end with a
realistic sample file (httpOnly sessionid preserved correctly,
cross-platform cookies correctly excluded by domain filter, CDP injection
into Cloak works against the imported cookies).

Same underlying constraint as before, still respected: login happens in
the client's own real, unrelayed browser tab. The only thing that changed
is which tool reads the resulting cookie - a widely-trusted, already-
approved extension instead of our own unpublished one.

## Resolved: real Cloak Browser, not a placeholder (2026-07-11)

`cloak/entrypoint.sh` previously ran stock `chromium` (apt package) with
manual flags - a placeholder noted as such in update 2 below. That's
replaced: `cloakbrowser` (pip) + `python -m cloakbrowser install` at build
time now fetches the actual [CloakHQ/CloakBrowser](https://github.com/CloakHQ/cloakbrowser)
binary (free tier: Chromium v146, 58 source-level fingerprint/CDP-detection
patches, no license key required), and `entrypoint.sh` execs that binary
directly with the same CDP flags as before. Verified: build downloads and
Ed25519-signature-verifies the binary, container boots it, CDP cookie
injection (`Network.setCookies`) works against it end to end.

Correction to earlier reasoning in this file: Cloak Browser's patches
specifically include "CDP input behavior mimicking" and a `humanize` mode
(Bézier mouse curves, natural typing rhythm) aimed at making CDP-relayed
interaction not look CDP-relayed - that's a real, specific mitigation for
the class of problem that CAPTCHA-locked the old build. It doesn't change
the Cookie Grant Flow decision above, though: Cloak Browser's own docs
don't claim to handle 2FA/new-device-verification/login flows, and
explicitly recommend persistent profiles with pre-warmed cookies for
exactly the "fresh session gets challenged" problem - i.e. their own
recommended pattern *is* the extension-based cookie injection already
built, not an alternative to it. Where Cloak Browser's stealth actually
matters most is everything after login: the ongoing automated activity
(CoSidekick posting/engaging, feed aggregation) is exactly the
"post-login automation that shouldn't look automated" problem it's built
to solve.

**Business model, clarified 2026-07-11:** free tier is the permanent
default, not a placeholder until Garry buys a license. Each client's
container runs its own free-tier Cloak Browser (unlimited sessions on the
free tier, per the vendor). Garry isn't buying, reselling, or centrally
budgeting for Cloak Browser access - what's being sold is the aggregator
(dashboard, QC, orchestration) on top of it. `CLOAKBROWSER_LICENSE_KEY` in
`docker-compose.yml`/`.env.example` stays as a per-deployment optional
knob - if an individual client wants to supply their own Pro key, that's
their cost, not LeLinc's.

## Handoff Log

Newest entry first.

### 2026-07-11 — Claude Code (sandbox session), update 6
Replaced the sideloaded-extension Connect flow with `import-cookies.html`
+ `POST /cookies/import` - see "Superseded" above. Also fixed two real
bugs found while verifying this end to end with real data (not
guessed): `run_sherlock()`'s output filter never matched Sherlock's actual
`[+] SiteName: url` format (matched zero lines since the first version of
this file - Sherlock has never returned a result before this), and
`RateLimitMiddleware` was throttling GETs too, so a dashboard page load's
two concurrent status fetches would randomly 429 one of them and render
as "not connected" even when the data existed. Both fixed; see README.md
Status for detail.

### 2026-07-11 — Claude Code (sandbox session), update 5
Swapped stock Chromium for the real Cloak Browser binary - see "Resolved:
real Cloak Browser" above.

### 2026-07-11 — Claude Code (sandbox session), update 4
Built the Cookie Grant browser extension (`extension/`) and wired it into
`nginx/dashboard.html` + `nginx/login-proxy/proxy.js`. See "Resolved:
Cookie Grant Flow mechanism" above - the reverse-proxy approach in
`q-specs` isn't what's being built, and here's what is instead. Also added
`nginx/extension-install.html` and a Dockerfile step that zips
`extension/` into `nginx/downloads/lelinc-extension.zip` for sideloading.

### 2026-07-11 — Claude Code (sandbox session), update 3
Corrected the framing above per Garry: Q orchestrates via its Claude Code
instance, it isn't a second independent builder. Restored the
implementation after the force-push (see "What happened" above) and
asked that `main` not be force-pushed going forward.

### 2026-07-11 — Claude Code (sandbox session), update 2
Re: Cloak Browser integration - `cloak/entrypoint.sh` and
`cloak/cdp_handler.py` in this repo right now are a generic-Chromium
placeholder, built only so the full flow had something to
integration-test against end to end. If Q's spec calls for the real
`cloakhq/cloakbrowser` image, that's a welcome update - two asks: keep the
CDP port internal-only (no VNC, no exposed debug port), and keep the
cookie-injection interface compatible with what `agents/cookie_grant.py`
writes to `/cookies/{client_id}/{platform}.json` (see that file for the
exact JSON shape).

### 2026-07-11 — Claude Code (sandbox session)
Scaffolded and verified end to end (local docker build/run, full
onboarding -> OSINT profiling -> QC -> report flow, rate limiter): docker
infra, Cookie Grant Agent, QC Engine, Orchestrator, NGINX dashboard/onboarding.
See README.md Status.

Still open from the original handoff: the browser extension that captures
login cookies from the client's real login tab isn't in this repo yet
(referenced by `nginx/login-proxy/proxy.js` but not built/ported here).
