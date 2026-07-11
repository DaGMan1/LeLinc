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

## Open concern: Cookie Grant Flow mechanism (2026-07-11)

`ARCHITECTURE.md` §1a ("Cookie Grant Flow — Detailed", from `q-specs`)
describes Step 1 as NGINX reverse-proxying the real Instagram login page
through our domain, and Step 3 as Cookie Grant monitoring that session via
CDP to detect login success and extract cookies. Flagging before this gets
implemented, not after:

- **If Cookie Grant can inspect the login session via CDP, that session is
  running in a CDP-controlled browser context** - not the client's own
  local Chrome. That means the client's login clicks/keystrokes are still
  going through some form of remote relay to reach that browser. This is
  the same input-timing problem that got Garry CAPTCHA-locked on Instagram
  before (see `[[project-lelinc-cookie-onboarding]]` if you have access to
  that memory) - reverse-proxying the login page's HTML doesn't change
  where the interaction actually happens.
- **A reverse proxy sitting between the client and Instagram's login POST
  can see the password in transit**, even if Cookie Grant is never
  designed to store it. "We never intercept the password" is true of the
  intent, not necessarily true of the network position - worth getting
  explicit about whether NGINX is doing opaque TCP/TLS passthrough (in
  which case it can't also detect login success via DOM/redirect
  inspection, contradicting Step 3) or terminating and re-rendering the
  page (in which case it can see the POST body).

Garry's original call (2026-07-09) was a browser extension precisely to
avoid both of these: real login happens in the client's own untouched
local browser, zero relay, zero proxy, and only the resulting cookies -
never credentials - get sent to LeLinc. That's not implemented in `main`
yet either (see below) - it's flagged as the open question, not assumed
as the answer. Q, if there's a way to make the proxy approach work that
doesn't reintroduce the relay-timing problem, that'd be great to spell
out - otherwise this probably needs to go back to Garry to decide before
either of us builds against it.

## Handoff Log

Newest entry first.

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
