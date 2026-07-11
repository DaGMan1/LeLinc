# LeLinc — Complete System Architecture

**Version:** 1.0 · **Date:** 11 July 2026
**Repo:** DaGMan1/LeLinc

---

## PRODUCT HIERARCHY

```
LeLinc ─── The Engine
  ├── CoSidekick  ─── Social engagement product (built on LeLinc)
  ├── Eyes On Chat ─── Comms layer product (built on LeLinc)
  └── [Future products built on LeLinc]

Key View Infrastructure ─── Internal engine for KVC + KVD
  ├── Serves KVC (consulting: restructuring, tax, strategy)
  ├── Serves KVD (digital: LeLinc products, PR, sales)
  ├── Uses LeLinc profiling for prospect scoping
  └── Eats its own dog food — we use our own stack
```

LeLinc is the engine. Key View Infrastructure is the internal business layer that powers both KVC and KVD. One shared LeLinc instance for profiling/scoping. Per-client containers only for paying customers.

---

## 1. THE FULL FLOW — End to End

```
┌─────────────────────────────────────────────────────────────────────────┐
│  KEY VIEW INFRASTRUCTURE — INTERNAL                                     │
│  (shared LeLinc instance for all scoping/prospecting)                   │
│                                                                         │
│  Prospecting — finds leads via news scraping, directory scraping,       │
│  social monitoring. Profiles each lead through LeLinc. Reports to       │
│  Garry for review.                                                      │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 1 — ONBOARDING (prospect converted to client)                   │
│                                                                         │
│  Client arrives at keyview.digital/lelinc                              │
│        │                                                                │
│        ▼                                                                │
│  ┌─────────────────────────────────────────┐                            │
│  │  ONBOARDING FORM (3 fields)             │                            │
│  │  • Business Name                        │                            │
│  │  • Domain / Website                     │                            │
│  │  • Email Address                        │                            │
│  └──────────────┬──────────────────────────┘                            │
│                 │ 1 click                                                │
│                 ▼                                                        │
│  ┌─────────────────────────────────────────┐                            │
│  │  CONTAINER SPINNED UP                   │                            │
│  │  Docker container with:                 │                            │
│  │  • NGINX (serves dashboard)             │                            │
│  │  • Cloak Browser (headless LeLinc)      │                            │
│  │  • Orchestrator Agent                   │                            │
│  │  • QC Agent                             │                            │
│  │  • Cookie Grant Agent                   │                            │
│  └─────────────────────────────────────────┘                            │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 2 — CLIENT PROFILING                                             │
│                                                                         │
│  Orchestrator begins profiling                                          │
│        │                                                                │
│        ▼                                                                │
│  ┌─────────────────────────────────────────┐                            │
│  │  LELINC PROFILING ENGINE                │                            │
│  │  Runs via Cloak Browser + rotating      │                            │
│  │  residential proxies                    │                            │
│  │                                         │                            │
│  │  Tools used (all CLI/integratable):     │                            │
│  │  • Sherlock       (username search)     │                            │
│  │  • Hunter.io      (email/domain check)  │                            │
│  │  • Epieos         (Google identity)     │                            │
│  │  • HIBP           (breach check)        │                            │
│  │  • Site scraping  (business profiles)   │                            │
│  │  • News scraping  (industry coverage)   │                            │
│  │  • Biz directory  (prospect discovery)  │                            │
│  │                                         │                            │
│  │  Rate limiting: max 1 req/3 sec per IP  │                            │
│  │  Proxy rotation: new IP per batch       │                            │
│  └──────────────┬──────────────────────────┘                            │
│                 │                                                        │
│                 ▼                                                        │
│  ┌─────────────────────────────────────────┐                            │
│  │  QC AGENT — CROSS-REFERENCE             │                            │
│  │  • Instagram found? ✓ bio + email match │                            │
│  │  • Facebook found? ✓ name + location    │                            │
│  │  • LinkedIn found? ✓ domain + industry  │                            │
│  │  • Prospect viable?  ✓ distress + needs │                            │
│  │                                         │                            │
│  │  Confidence scoring:                    │                            │
│  │  2/3 sources = HIGH                     │                            │
│  │  1/3 sources = POSSIBLE (flagged)       │                            │
│  │  0/3 sources = NOT FOUND                │                            │
│  └──────────────┬──────────────────────────┘                            │
│                 │                                                        │
│                 ▼                                                        │
│  ┌─────────────────────────────────────────┐                            │
│  │  REPORT TO GARRY                        │                            │
│  │  • For KVC: financial signals, distress │                            │
│  │  • For KVD: platform presence, gaps     │                            │
│  │  • Lead score + rationale               │                            │
│  │  • Media contact list + reach           │                            │
│  │                                         │                            │
│  │  Garry reviews. Garry decides what to   │                            │
│  │  share with the client.                 │                            │
│  └─────────────────────────────────────────┘                            │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 3 — PLATFORM CONNECTION (one at a time)                          │
│                                                                         │
│  Client sees report → picks a platform                                  │
│        │                                                                │
│        ▼                                                                │
│  ┌─────────────────────────────────────────┐                            │
│  │  COOKIE GRANT FLOW                      │                            │
│  │                                         │                            │
│  │  1. NGINX serves real login page        │                            │
│  │  2. Client logs in normally             │                            │
│  │  3. Cookie Grant Agent extracts session │                            │
│  │  4. Login tab closes                    │                            │
│  │  5. Cloak loads cookies = logged in     │                            │
│  │  6. Platform shows as "Connected"       │                            │
│  └─────────────────────────────────────────┘                            │
│                                                                         │
│  Repeat for next platform. Never bulk.                                  │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  PHASE 4 — LIVE                                                         │
│                                                                         │
│  ┌────────────────────────┐  ┌─────────────────────┐                   │
│  │  CoSidekick            │  │  Eyes On Chat       │                   │
│  │  • Posts on schedule   │  │  • Client comms      │                   │
│  │  • Engages audience    │  │  • Support tickets    │                   │
│  │  • Monitors activity   │  │  • Q oversight       │                   │
│  │  • Reports back        │  │                     │                   │
│  └────────────────────────┘  └─────────────────────┘                   │
│                                                                         │
│  Dashboard shows everything in real-time                               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 1a. Cookie Grant Flow — Detailed

This is the mechanism Claude Code needs to build. It explains how cookies move from the client's real browser into Cloak without ever storing a password.

### The Problem
Cloak Browser needs to be logged into social platforms to work. But Cloak can't log in itself — login pages use 2FA, CAPTCHAs, and suspicious-login detection. The only way to get an authenticated session is to have a real human log in once, then hand the session to Cloak.

### The Solution: Cookie Grant

**Step 1 — Client clicks "Connect Instagram" on the LeLinc dashboard**
- NGINX serves a page at `/connect/instagram` that proxies to the real Instagram login page
- The client sees the genuine Instagram login page, served through a proxy on our domain
- The client never leaves lelinc.keyview.com.au — the login page looks and works exactly like Instagram's

**Step 2 — Client logs in normally**
- Client enters their Instagram username and password on the real Instagram login page
- The credentials go directly to Instagram's servers — NGINX just proxies the traffic
- **We never intercept, read, or store the password.** This is critical.
- Instagram processes the login and returns the authenticated session

**Step 3 — Cookie Grant detects the successful login**
- Cookie Grant monitors the browser session via CDP or DOM event
- It watches for the post-login redirect (feed URL, profile URL — the client is now logged in)
- On detecting success, it calls CDP `Network.getCookies()` to extract all session cookies
- These cookies contain the `sessionid`, `csrftoken`, and any other auth tokens Instagram set

**Step 4 — Cookies are stored**
- Cookie Grant writes the cookies as JSON: `/data/cookies/{client_id}/instagram.json`
- Format per cookie: `{name, value, domain, path, secure, httpOnly, expiry}`
- Cookies are stored per platform per client — fully isolated
- Never stored with any password or personal data

**Step 5 — Login tab closes**
- Cookie Grant sends a signal to the dashboard: login complete
- The login tab closes
- The client sees the platform listed as "Connected" on their dashboard

**Step 6 — Cloak loads the cookies**
- On next container startup (or immediately), Cloak's `entrypoint.sh` reads the cookie files
- For each cookie, it calls CDP `Network.setCookie(cookie)` to inject it into Cloak's session
- After all cookies are set, Cloak refreshes the page
- Cloak now has an authenticated session — it's wearing the client's login
- Cloak never sees a login page, never triggers 2FA, never triggers suspicious-login alerts

### Cookie Expiry and Reconnection

- Instagram sessions last ~2-8 weeks, TikTok ~1-3 months, LinkedIn ~30 days
- When Cloak performs an action and gets a login redirect or 401, Cookie Grant detects the expired session
- Dashboard shows: "🔴 Instagram session expired — reconnect"
- Client clicks "Reconnect" → same Cookie Grant flow from Step 1
- Old cookies are deleted, new cookies captured, Cloak restarts with fresh session
- Cookie Grant logs expiry dates and can proactively warn before expiry

### Design Principles
- **No passwords ever stored** — session cookies only, never credentials
- **One platform at a time** — login flow is serial per platform, never bulk
- **Isolated per container** — Client A's container has only Client A's cookies
- **Stateless service** — Cookie Grant is a stateless FastAPI service (~50 lines)
- **Minimal surface** — Cookie Grant only has 2 endpoints: POST /cookies and GET /cookies/{client_id}
- **No user database** — no registration, no user management, just cookie storage

---

## 2. SOFTWARE STACK

| Layer | Software | Purpose |
|---|---|---|
| **Container Runtime** | Docker | One container per client |
| **Frontend** | NGINX | Dashboard, onboarding, login pages |
| **LeLinc Browser** | Cloak Browser (Chromium) | Social media actions via CDP |
| **Proxy** | Rotating residential proxy pool | No IP blacklisting |
| **Cookie Grant** | Custom FastAPI (~50 lines) | Receive/store/feed cookies |
| **Orchestrator** | Python + small LLM | Run profiling flow |
| **QC** | Python rules engine | Cross-reference + confidence |
| **Sherlock** | Python CLI | Username search (400+ platforms) |
| **Hunter.io** | API | Domain email discovery |
| **Epieos** | Web/API | Google identity by email |
| **HIBP** | API | Breach/compromise check |
| **News scraping** | Python + Cloak | Industry coverage |
| **Directory scraping** | Python + Cloak | Prospect discovery |
| **CoSidekick** (product) | LLM (Qwen/Claude) | Engagement (optional tier on LeLinc) |
| **Eyes On Chat** (product) | FastAPI + WebSocket | Client comms (optional tier on LeLinc) |

---

## 3. DOCKER CONTAINER STRUCTURE

```
lelinc-client-container/
├── nginx/
│   ├── Dockerfile
│   ├── dashboard.html           # Client dashboard UI
│   ├── onboarding.html          # Onboarding form
│   └── login-proxy/             # Proxies real login pages
├── cloak/
│   ├── Dockerfile
│   ├── entrypoint.sh            # Loads cookies, starts Cloak
│   └── cdp_handler.py           # CDP command interface
├── agents/
│   ├── orchestrator.py          # Small LLM — runs the LeLinc flow
│   ├── qc_engine.py             # No LLM — cross-reference + confidence
│   └── cookie_grant.py          # No LLM — cookie service
├── docker-compose.yml           # Single container (NGINX + Cloak + agents)
└── start.sh                     # Entry command
```

---

## 4. HOW KVC AND KVD SHARE THE SAME INFRASTRUCTURE

```
Key View Infrastructure (shared LeLinc instance)
        │
        ├── Internal prospecting engine (prospecting, profiling)
        │
        ├── KVC Client
        │   • LeLinc profile → financial distress signals
        │   • Report generated for Garry
        │   • Container only if they become a client
        │
        └── KVD Client
            • LeLinc profile → social presence, gaps
            • Report generated for Garry
            • Container only if they become a CoSidekick/LeLinc client
```

Both use the same profiling engine. The reports just focus on different signals depending on which business needs them.

---

## 5. FALSE POSITIVE PREVENTION

Every platform claim must pass **at least 2 of 3** checks:

```
Instagram:
  □ Username resolves on Instagram search
  □ Email in breach data linked to handle
  □ Business domain in bio or posts
  → 2/3 = HIGH CONFIDENCE

LinkedIn:
  □ Name + company match
  □ Domain in company description
  □ Email format matches @company.com.au
  → 2/3 = HIGH CONFIDENCE

Prospect viability (KVC):
  □ Financial distress signals found
  □ Business actively trading
  □ Owner/decision-maker identified
  → 2/3 = WORTH PURSUING
```

Anything with less than 2 sources is **never shown** to client. Flagged internally only.

---

## 6. EAT YOUR OWN DOG FOOD

Before we sell it, we use it:

| What we do | How LeLinc helps |
|---|---|
| Profile KVC prospects | LeLinc profiling engine |
| Find new business leads | Prospecting engine |
| Manage our own social presence | CoSidekick on our own accounts |
| Client comms | Eyes On Chat |
| Monitor press coverage | News scraping |
| Qualify leads with confidence | QC Engine |

---

## 7. API ENDPOINTS

| Method | Endpoint | Service | Description |
|---|---|---|---|
| POST | /onboard | Orchestrator | Submit new client for profiling |
| GET | /onboard/{id}/status | Orchestrator | Check profiling progress |
| POST | /cookies | Cookie Grant | Submit captured cookies |
| GET | /cookies/{client_id} | Cookie Grant | List connected platforms |
| POST | /qc/check | QC Engine | Verify a claim |
| GET | /dashboard | NGINX | Client dashboard UI |
| GET | /health | All | Health check |

---

## 8. KEY CONSTRAINTS

- **Single container per client** — don't split services across containers
- **No passwords stored** — Cookie Grant captures session cookies, not credentials
- **One platform at a time** — login flow is serial, not bulk
- **2-of-3 rule** — every claim verified by at least 2 independent sources
- **Rate limit** — max 1 request per 3 seconds per IP
- **Cloak Browser** — not Playwright, not Puppeteer, not Selenium

---

## 9. DEPLOYMENT

- Runs on VPS (2.25.187.99) behind Caddy reverse proxy
- Domain: lelinc.keyview.com.au
- Ports: 80 (dashboard), 6901 (Cloak), 8000+ (services)
- Cloak Browser already running at lelinc.keyview.com.au:8081