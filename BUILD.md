# LeLinc — Build Handoff for Claude Code

**Priority:** HIGH — this is the core engine for Key View Digital
**Date:** 11 July 2026
**Handoff from:** Q (Overseer)

## What You Need to Build

LeLinc is a social media automation engine. It runs inside Docker containers — one container per client. Each container has:

1. **NGINX** — serves the client dashboard, onboarding form, and login proxies
2. **Cloak Browser** — headless Chromium that does the actual social media work
3. **Cookie Grant Agent** — tiny FastAPI service that captures login cookies and feeds them to Cloak
4. **QC Engine** — Python rules engine that cross-references findings (2-of-3 rule)
5. **Orchestrator** — Python script that runs the profiling flow

## Files to Create

### 1. Project Root

```
/Users/garry/Projects/lelinc/
├── docker-compose.yml
├── Dockerfile
├── start.sh
├── nginx/
│   ├── default.conf
│   ├── dashboard.html
│   ├── onboarding.html
│   └── login-proxy/
│       └── proxy.js
├── cloak/
│   ├── entrypoint.sh
│   └── cdp_handler.py
├── agents/
│   ├── orchestrator.py
│   ├── qc_engine.py
│   ├── cookie_grant.py
│   ├── pr_manager.py
│   ├── sales_manager.py
│   └── sales_agent.py
└── README.md
```

### 2. Docker Configuration

**docker-compose.yml** — single container setup with ports:
- 80 (NGINX dashboard UI)
- 6901 (noVNC for Cloak)
- 8000 (Cookie Grant API)
- 8001 (Orchestrator API)

**Dockerfile** — based on Python 3.12-slim:
- Install NGINX, Cloak Browser, Python dependencies
- Copy all agent files
- Entrypoint starts NGINX + Cookie Grant + Cloak

### 3. Core Services

**Cookie Grant Agent** (cookie_grant.py — no LLM):
- FastAPI endpoint POST /cookies {cookies: string, platform: string, client_id: string}
- Stores as JSON: /cookies/{client_id}/{platform}.json
- Feed method: Cloak CDP via Network.setCookie
- Monitor cookie expiry — notify on expiry
- Endpoint GET /cookies/status/{client_id} — what platforms are connected, expiry dates

**QC Engine** (qc_engine.py — no LLM):
- Pure Python rules engine
- Input: claim type + up to 3 sources
- Output: CONFIRMED (3/3) / HIGH (2/3) / POSSIBLE (1/3) / FALSE (0/3)
- Rules defined for: Instagram, LinkedIn, Facebook, TikTok, Financial distress, Business viability
- Endpoint POST /qc/check {claim_type: string, sources: string[]}

**Orchestrator** (orchestrator.py):
- Python script that runs the LeLinc profiling flow
- 1. Receive client info (name, domain, email)
- 2. Run OSINT tools (Sherlock, Hunter.io via API, HIBP via API)
- 3. Collect results
- 4. Hand to QC Engine for cross-reference
- 5. Generate client profile report
- 6. Return report

### 4. NGINX Frontend

**Dashboard** (dashboard.html):
- Shows client's connected platforms and status
- "Connect Instagram/LinkedIn/TikTok" buttons → launches Cookie Grant login proxy
- Shows profile report when available
- Mobile-first, dark theme, Key View Digital branding

**Onboarding** (onboarding.html):
- 3 fields: Business Name, Domain/Website, Email Address
- Submit → POST to Orchestrator to start profiling
- Shows progress spinner while profiling runs

### 5. Cloak Integration

**entrypoint.sh**:
- Load cookies from /cookies/{client_id}/{platform}.json
- Start Cloak Browser with those cookies injected
- Expose CDP port 6901

**cdp_handler.py**:
- CDP command interface for Cloak
- Navigate, screenshot, click, type
- Platform-specific action templates (Instagram: like/comment, LinkedIn: connect/message, etc.)

## Build Order

1. **docker-compose.yml + Dockerfile** — get the container running with NGINX + Cloak
2. **Cookie Grant Agent** — cookie capture, store, feed to Cloak
3. **QC Engine** — rules engine, 2-of-3 verification
4. **Orchestrator** — profiling flow, OSINT integrations
5. **NGINX frontend** — dashboard + onboarding UI
6. **Testing** — full flow: onboarding → profiling → QC → report

## Key Constraints

- **Single container per client** — don't split services across containers
- **No passwords stored** — Cookie Grant captures session cookies, not credentials
- **One platform at a time** — login flow is serial, not bulk
- **2-of-3 rule** — every claim verified by at least 2 independent sources
- **Rate limit** — max 1 request per 3 seconds per IP
- **Cloak Browser** — use cloak browser, not Playwright/Puppeteer

## Tools Already on the VPS

- Cloak Browser running at lelinc.keyview.com.au:8081
- Docker installed
- Python 3.12
- Caddy reverse proxy configured
- ZeroTier 10.35.94.211

## API Structure

| Endpoint | Method | Service | Description |
|---|---|---|---|
| /onboard | POST | Orchestrator | Submit new client for profiling |
| /onboard/status/:id | GET | Orchestrator | Check profiling progress |
| /cookies | POST | Cookie Grant | Submit captured cookies |
| /cookies/status/:client_id | GET | Cookie Grant | Check connected platforms |
| /qc/check | POST | QC Engine | Verify a claim |
| /dashboard | GET | NGINX | Client dashboard UI |
| /health | GET | All | Health check |

## How KVC + KVD Use This

Same LeLinc engine. Different report formats:
- **KVC**: focus on financial distress signals, director changes, ASIC notices
- **KVD**: focus on social media presence gaps, website quality, engagement metrics

Reports are generated by the Orchestrator and passed to the QC Engine before being shown to Garry.