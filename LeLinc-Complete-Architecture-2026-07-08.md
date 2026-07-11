# LeLinc — Engine Architecture & Build Spec

**Version:** 1.0 · **Date:** 11 July 2026
**Repo:** DaGMan1/LeLinc

---

## What Is LeLinc

LeLinc is a **Docker container** that runs Cloak Browser (stealth Chromium) plus a set of lightweight services that together let an AI agent interact with social media platforms on behalf of a client.

Each client gets their own container. The container does not run an LLM — it's a tool layer. An external agent (or human) drives it via API.

---

## The Container

```
┌─────────────────────────────────────────┐
│  LELINC CONTAINER (one per client)      │
│                                         │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │  NGINX       │  │  Cloak Browser   │  │
│  │  • Dashboard │  │  (stealth Chrom) │  │
│  │  • Onboarding│  │  • CDP endpoint  │  │
│  │  • Login Pxy │  │  • Cookie feed   │  │
│  └─────────────┘  └──────────────────┘  │
│                                         │
│  ┌──────────────┐  ┌──────────────────┐  │
│  │  Cookie Grant│  │  QC Engine       │  │
│  │  (FastAPI)   │  │  (Rules Engine)  │  │
│  │  • Capture   │  │  • 2-of-3 verify │  │
│  │  • Store     │  │  • Confidence    │  │
│  │  • Feed Cloak│  │  • False pos kill│  │
│  └──────────────┘  └──────────────────┘  │
│                                         │
│  ┌──────────────────────────────────┐   │
│  │  Orchestrator (Python)          │   │
│  │  • Profiling flow (if used)     │   │
│  │  • API endpoints                │   │
│  └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## Services

### 1. Cloak Browser
- Stealth Chromium 146 via `cloakhq/cloakbrowser` Docker image
- Exposes CDP endpoint for programmatic control
- Cookie injection: cookies loaded at startup from Cookie Grant
- NoVNC on port 6901 for visual debugging
- CDP frontend on /browser/

### 2. Cookie Grant Agent
- Tiny FastAPI service (~50 lines)
- Endpoint: POST /cookies {cookies, platform, client_id}
- Stores as JSON: /cookies/{client_id}/{platform}.json
- Injects into Cloak on startup
- Monitors expiry — notifies dashboard when session needs refresh

### 3. QC Engine
- Pure Python rules engine (no LLM)
- Endpoint: POST /qc/check {claim_type, sources[]}
- Returns: CONFIRMED / HIGH / POSSIBLE / FALSE
- Rules for: Instagram, LinkedIn, Facebook, TikTok, Business data
- 2-of-3 verification rule

### 4. Orchestrator
- Python script that runs a profiling flow
- Endpoint: POST /onboard {name, domain, email}
- Runs OSINT tools (Sherlock, Hunter.io, HIBP)
- Collates results, sends to QC Engine
- Returns: profile report JSON

### 5. NGINX
- Dashboard UI — shows connected platforms, status, reports
- Onboarding form — 3 fields (business name, domain, email)
- Login proxy — serves real platform login page for Cookie Grant

## API Endpoints

| Method | Endpoint | Service | Description |
|---|---|---|---|
| POST | /onboard | Orchestrator | Start profiling a client |
| GET | /onboard/{id}/status | Orchestrator | Check profiling status |
| POST | /cookies | Cookie Grant | Submit captured cookies |
| GET | /cookies/{client_id} | Cookie Grant | List connected platforms |
| POST | /qc/check | QC Engine | Verify a claim |
| GET | /dashboard | NGINX | Client dashboard UI |
| GET | /health | All | Health check |

## File Structure

```
lelinc-container/
├── docker-compose.yml
├── Dockerfile
├── start.sh
├── nginx/
│   ├── default.conf
│   ├── dashboard.html
│   ├── onboarding.html
│   └── login-proxy/
├── cloak/
│   ├── entrypoint.sh
│   └── cdp_handler.py
├── agents/
│   ├── orchestrator.py
│   ├── qc_engine.py
│   └── cookie_grant.py
└── README.md
```

## Key Constraints

- **Single container per client** — don't split services
- **No passwords stored** — Cookie Grant captures session cookies only
- **One platform at a time** — login is serial, not bulk
- **2-of-3 rule** — every claim verified by at least 2 independent sources
- **Rate limit** — max 1 request per 3 seconds per IP
- **Cloak Browser** — not Playwright, not Puppeteer, not Selenium

## Deployment

Runs on the VPS (2.25.187.99) behind Caddy reverse proxy.
Domain: lelinc.keyview.com.au
Ports: 80 (dashboard), 6901 (Cloak), 8000+ (services)