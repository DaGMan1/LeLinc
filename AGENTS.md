# AGENTS.md — Working Agreement for This Repo

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

## Handoff Log

Newest entry first.

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
