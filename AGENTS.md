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

## Ownership split (decided by Garry, 2026-07-11)

Both instances keep building, divided by area:

- **VPS instance (Q-directed) owns Cloak Browser integration** — it's
  co-located with the real Cloak Browser deployment
  (`lelinc.keyview.com.au:8081`, `cloakhq/cloakbrowser` image) and can
  actually test against it. Owns: `cloak/entrypoint.sh`,
  `cloak/cdp_handler.py`, and the Cloak-specific layer of the Dockerfile
  (base image / install steps for Cloak Browser itself).
- **This session owns everything else** — `agents/orchestrator.py`,
  `agents/qc_engine.py`, `agents/cookie_grant.py` (the storage/API side;
  the CDP feed-into-Cloak call is the VPS instance's territory since it
  touches Cloak directly), `agents/rate_limit.py`, `nginx/` (dashboard,
  onboarding, default.conf, login-proxy), and the overall
  `docker-compose.yml` / `start.sh` shape (ports, service orchestration).
- **Non-negotiable regardless of area:** no VNC/noVNC anywhere. This is
  Garry's explicit product decision, not an implementation detail either
  side can relitigate unilaterally.
- **API contract is shared surface** — changing an endpoint path affects
  the other side's code. Propose changes in the Handoff Log first; don't
  silently rename and push. Today's implemented-and-tested paths
  (`GET /cookies/status/{client_id}`, `GET /onboard/status/{id}`) are
  canonical until changed here with agreement.

## Ground rules

1. **Pull with `--ff-only` before every push.** If it's not a fast-forward,
   stop and reconcile rather than force-pushing over the other agent.
2. **Stay inside your area.** If you need a change on the other side, ask
   for it in the Handoff Log instead of editing those files directly.
3. **State the "why" in commit messages** — neither agent has memory of
   the other's conversation, only git history and this file.
4. **`README.md`'s Status section is the single source of truth** for
   what's actually built and working (verified end to end, not just
   written) vs still pending.

## Handoff Log

Newest entry first.

### 2026-07-11 — Claude Code (sandbox session), update 2
Garry decided: split by area, both instances keep building (see Ownership
split above). VPS instance: please treat `cloak/entrypoint.sh` and
`cloak/cdp_handler.py` as yours to rework against the real
`cloakhq/cloakbrowser` image - the versions currently in this repo are my
generic-Chromium placeholder, built only so the full flow had something
to integration-test against end to end. Replace them freely. Two asks:
keep the CDP port internal-only (no VNC, no exposed debug port), and keep
`load_client_cookies()` / the cookie-injection entrypoint's interface
compatible with what `agents/cookie_grant.py` writes to
`/cookies/{client_id}/{platform}.json` (see that file for the exact JSON
shape) so I don't have to change the storage side to match.

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
