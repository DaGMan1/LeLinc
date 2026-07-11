# AGENTS.md — Working Agreement for This Repo

This repo has at least two AI agents pushing directly to `main`, with no
live channel between them:

- **This Claude Code instance** — runs in a sandboxed session Garry drives
  directly, connected via a repo-scoped deploy key.
- **Another Claude Code instance** — runs on the VPS at
  `/home/claude-user/lelinc-repo/`, commits as `claude-code@lelinc.dev`,
  appears to be directed by Q.

Coordination happens through this file, commit messages, and the Handoff
Log below. Read this file before making changes.

## Known divergence (2026-07-11)

The two instances built different specs before discovering each other.
Not yet reconciled:

- **Cloak Browser implementation** — this session's `cloak/entrypoint.sh`
  uses stock Chromium + Xvfb. The VPS instance's `LeLinc-Complete-Architecture-2026-07-08.md`
  specs the `cloakhq/cloakbrowser` image instead.
- **noVNC** — `BUILD.md` (VPS instance's version) re-adds a noVNC port
  (6901). This session's build deliberately drops it — Garry explicitly
  rejected noVNC/remote-desktop approaches for LeLinc's browser layer on
  the prior build ("it is slow it is clunky it does not work"). Treat "no
  VNC anywhere" as the standing decision unless Garry says otherwise here.
- **Endpoint naming** — `GET /cookies/status/{client_id}` vs
  `GET /cookies/{client_id}`; `GET /onboard/status/{id}` vs
  `GET /onboard/{id}/status`. This session's code (`agents/cookie_grant.py`,
  `agents/orchestrator.py`) currently implements the `/status/` form.

## Ground rules (proposed by this session, open to revision)

1. **Pull with `--ff-only` before every push.** If it's not a fast-forward,
   stop and reconcile rather than force-pushing over the other agent.
2. **Docs vs code split, for now:** Q's instance owns architecture/spec
   docs (`ARCHITECTURE.md`, `BUILD.md`, etc.); this session owns the
   implementation (`agents/`, `cloak/`, `nginx/`, `Dockerfile`,
   `docker-compose.yml`). If the spec changes in a way that requires a
   code change, leave a note in the Handoff Log instead of editing code
   files directly from the other side — the note gets picked up and
   implemented deliberately, not blind-applied.
3. **State the "why" in commit messages** — neither agent has memory of
   the other's conversation, only git history and this file.
4. **`README.md`'s Status section is the single source of truth** for
   what's actually built and working (verified end to end, not just
   written) vs still pending.

## Handoff Log

Newest entry first.

### 2026-07-11 — Claude Code (sandbox session)
Scaffolded and verified end to end (local docker build/run, full
onboarding -> OSINT profiling -> QC -> report flow, rate limiter): docker
infra, Cookie Grant Agent, QC Engine, Orchestrator, NGINX dashboard/onboarding.
See README.md Status.

Flagging the divergence above for reconciliation. Until Garry says
otherwise: no VNC anywhere, and the `/status/` endpoint paths in the code
right now are what's actually implemented and tested — treat BUILD.md's
renamed paths as proposed, not yet applied.

Also still open from the original handoff: the browser extension that
captures login cookies from the client's real login tab isn't in this
repo yet (referenced by `nginx/login-proxy/proxy.js` but not built/ported
here).
