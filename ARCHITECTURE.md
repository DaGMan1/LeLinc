# LeLinc — Complete System Architecture & Flow

**Version:** 2.0 · **Date:** 8 July 2026
**Branding:** Key View Digital (legal entity)
**Saved By:** Q

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
│  ┌─────────────────────────────────────────────────────────┐           │
│  │  PROSPECTING (PR Manager + Sales Manager)               │           │
│  │                                                         │           │
│  │  PR Manager:                                            │           │
│  │  • Scrapes news/journals for industry coverage          │           │
│  │  • Identifies journalists writing about KVC/KVD topics  │           │
│  │  • Tracks competitor mentions and press                 │           │
│  │  • Builds media contact list per industry               │           │
│  │                                                         │           │
│  │  Sales Manager:                                         │           │
│  │  • Scrapes businesses matching KVC/KVD target profile   │           │
│  │  • Finds businesses with weak social presence (= need)  │           │
│  │  • Identifies distressed companies (= KVC opportunity)  │           │
│  │  • Builds lead list for Sales Agent                     │           │
│  │                                                         │           │
│  │  Sales Agent:                                           │           │
│  │  • Works leads from Sales Manager                       │           │
│  │  • Runs LeLinc profile on each prospect                 │           │
│  │  • Generates CosmetologyCo-style report                 │           │
│  │  • Hands report to Garry for review                     │           │
│  └─────────────────────────────────────────────────────────┘           │
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
│  Orchestrator Agent begins profiling                                    │
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
│  │  • News scraping  (PR Manager)          │                            │
│  │  • Biz directory  (Sales Manager)       │                            │
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
│  │  • For Sales: lead score + rationale    │                            │
│  │  • For PR: journalist list + reach      │                            │
│  │                                         │                            │
│  │  You review. You decide what to share.  │                            │
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

## 2. THE FULL AGENT TEAM

| # | Agent | LLM? | Role | Business |
|---|---|---|---|---|
| **1** | **Orchestrator** | ✅ Small | Runs LeLinc flow front-to-back. Profiling, tools, state, errors. | Core |
| **2** | **QC Agent** | ❌ None | Cross-references findings. Confidence scoring. Kills false positives. | Core |
| **3** | **Cookie Grant** | ❌ None | Captures login sessions, stores per-platform, feeds to Cloak. | Core |
| **4** | **PR Manager** | ✅ LLM | Scrapes news, tracks journalists, builds media lists, monitors competitor press. | KVD |
| **5** | **Sales Manager** | ✅ LLM | Scrapes directories for prospects, scores leads, identifies opportunities. | KVD |
| **6** | **Sales Agent** | ✅ LLM | Works leads from Sales Manager, runs profiles, generates reports for Garry. | KVD |
| **7** | **CoSidekick** | ✅ Full | (Product) Engagement strategy, posting, monitoring on LeLinc. | KVD |
| **8** | **Q (Overseer)** | ✅ Full | Sees everything. Overview of all agents, all clients, all comms. | Key View |

---

## 3. SOFTWARE STACK

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
| **News scraping** | Python + Cloak | PR Manager — industry coverage |
| **Directory scraping** | Python + Cloak | Sales Manager — prospect discovery |
| **CoSidekick** (product) | LLM (Qwen/Claude) | Engagement (optional tier on LeLinc) |
| **Eyes On Chat** (product) | FastAPI + WebSocket | Client comms (optional tier on LeLinc) |

---

## 4. DOCKER CONTAINER STRUCTURE

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
│   ├── cookie_grant.py          # No LLM — cookie service
│   ├── pr_manager.py            # LLM — news scraping + media lists
│   ├── sales_manager.py         # LLM — prospect discovery + scoring
│   └── sales_agent.py           # LLM — profile generation + reports
├── docker-compose.yml           # Single container (NGINX + Cloak + agents)
└── start.sh                     # Entry command
```

---

## 5. HOW KVC AND KVD SHARE THE SAME INFRASTRUCTURE

```
Key View Infrastructure (shared LeLinc instance)
        │
        ├── Internal prospecting engine (PR, Sales, profiling)
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

## 6. FALSE POSITIVE PREVENTION

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

## 7. EAT YOUR OWN DOG FOOD

Before we sell it, we use it:

| What we do | How LeLinc helps |
|---|---|
| Profile KVC prospects | LeLinc profiling engine |
| Find new business leads | Sales Manager + Sales Agent |
| Manage our own social presence | CoSidekick on our own accounts |
| Client comms | Eyes On Chat |
| Monitor press coverage | PR Manager |
| Qualify leads with confidence | QC Agent |

---

## 8. LINKED ARCHITECTURE DOCS

- `_Shared/Resources/LeLinc-Architecture-2026-07-08.md` — Core architecture
- `_Shared/Resources/FBI-OSINT-Tools-2026-06-24.md` — OSINT tool reference
- `_Shared/Resources/10-Best-Free-AI-Agent-Tools-Hermes-Featured-2026-06-18.md` — Agent tooling reference
- `_Shared/crm/` — Client records for alpha testers
- `_Shared/Resources/agency-agents/` — MIT-licensed specialist agent library (pinned)