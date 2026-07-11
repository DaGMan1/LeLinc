# LeLinc — Build Handoff for Claude Code

**Priority:** HIGH
**Repo:** DaGMan1/LeLinc
**Date:** 11 July 2026

## What to Build

LeLinc is a Docker container that runs Cloak Browser (stealth Chromium) plus supporting services for social media profiling and automation. One container per client.

See ARCHITECTURE.md for full system design.

## The Full Flow

The LeLinc engine operates in 4 phases. Build them in this order:

### Phase 1 — Onboarding
- 3-field form: Business Name, Domain/Website, Email Address
- One click spins up a container with NGINX + Cloak + agents
- Dashboard served to client

### Phase 2 — Client Profiling
- Orchestrator runs profiling via Cloak Browser + rotating proxies
- Tools: Sherlock (username search), Hunter.io (email), Epieos (Google identity), HIBP (breach check), site scraping, news scraping, business directory scraping
- Rate limit: 1 req/3s per IP
- QC Engine cross-references every finding (2-of-3 rule)
- Report generated for Garry

### Phase 3 — Platform Connection
- Cookie Grant flow: client logs in normally → cookies extracted → fed to Cloak
- One platform at a time, never bulk
- Dashboard shows "Connected" status

### Phase 4 — Live
- CoSidekick and Eyes On Chat are products built on top of LeLinc
- Not part of the engine build — build the platform first

## Build Order

1. **docker-compose.yml + Dockerfile** — single container, NGINX + Cloak + Python services
2. **Cookie Grant Agent** — cookie capture, store, feed to Cloak
3. **QC Engine** — 2-of-3 rules engine per platform
4. **Orchestrator** — profiling flow + OSINT integrations
5. **NGINX frontend** — dashboard + onboarding UI
6. **Testing** — full flow: onboard → profile → QC → report

## What Already Exists on the VPS

- Cloak Browser running at lelinc.keyview.com.au:8081
- Docker installed
- Python 3.12
- Caddy reverse proxy configured
- Existing lelinc directory at /home/claude-user/lelinc/ (old work)
- This repo at /home/claude-user/lelinc-repo/

## Key Constraints

- Single container per client
- No passwords stored — cookies only
- One platform at a time
- 2-of-3 rule for all verification
- Rate limit: 1 req/3s per IP
- Cloak Browser only — not Playwright/Puppeteer/Selenium

## API Structure

| Method | Endpoint | Service | Description |
|---|---|---|---|
| POST | /onboard | Orchestrator | Start profiling |
| GET | /onboard/{id}/status | Orchestrator | Check progress |
| POST | /cookies | Cookie Grant | Submit cookies |
| GET | /cookies/{client_id} | Cookie Grant | List connected |
| POST | /qc/check | QC Engine | Verify claim |
| GET | /dashboard | NGINX | UI |
| GET | /health | All | Health check |