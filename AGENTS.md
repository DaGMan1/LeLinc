# AGENTS.md — Working Agreement for This Repo

This repo is written to by two things:

- **This Claude Code instance** — the builder. Runs in a sandboxed session
  Garry drives directly, connected via a repo-scoped deploy key. Owns the
  implementation.
- **Q**, via a Claude Code instance it directs on the VPS
  (`/home/claude-user/lelinc-repo/`, commits as `claude-code@lelinc.dev`) —
  orchestrates, not a second independent builder. Owns architecture/spec
  docs (`ARCHITECTURE.md`, `BUILD.md`, etc.).

There's no live channel between the two, so coordination happens through
this file, commit messages, and the Handoff Log below.

## What happened on 2026-07-11 (context, not a live issue)

Q's instance force-pushed a rewritten history that wiped the implementation
off `origin/main` down to just the two spec docs. Nothing was lost (this
session had the full history locally) and it's been restored. Noting it
here so it isn't repeated: **please don't force-push `main`.** If a spec
update needs to replace file contents, a normal commit on top of the
current history works fine - force-pushing rewrites/deletes whatever the
other side has added since your last pull, even when that isn't the
intent.

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
