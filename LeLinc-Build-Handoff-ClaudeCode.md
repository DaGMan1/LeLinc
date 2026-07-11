# LeLinc — Build Handoff for Claude Code

**Priority:** HIGH
**Repo:** DaGMan1/LeLinc
**Date:** 11 July 2026

## What to Build

LeLinc is a Docker container that runs Cloak Browser (stealth Chromium) plus supporting services for social media automation. One container per client.

See ARCHITECTURE.md for full system design.

## Build Order

1. **docker-compose.yml + Dockerfile** — single container, NGINX + Cloak + Python services
2. **Cookie Grant Agent** — cookie capture/store/feed
3. **QC Engine** — 2-of-3 rules engine
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