import asyncio
import os
import re
import subprocess
import time
import uuid

import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agents.qc_engine import router as qc_router
from agents.rate_limit import RateLimitMiddleware

app = FastAPI(title="LeLinc Orchestrator")
app.add_middleware(RateLimitMiddleware, min_interval=3.0)
app.include_router(qc_router)

JOBS: dict[str, dict] = {}

HUNTER_API_KEY = os.environ.get("HUNTER_API_KEY")
HIBP_API_KEY = os.environ.get("HIBP_API_KEY")

# QC's 2-of-3 rule (agents/qc_engine.py) needs signals from multiple
# independent tools. Right now only Sherlock is unconditionally wired up
# (Hunter/HIBP need API keys, and the domain-in-bio/site-scraping signal
# isn't built at all) - so platform claims below report exactly one
# signal, never a fabricated confidence level. See PLATFORM_DOMAINS.
PLATFORM_DOMAINS = {
    "instagram": "instagram.com",
    "linkedin": "linkedin.com",
    "facebook": "facebook.com",
    "tiktok": "tiktok.com",
}


class OnboardRequest(BaseModel):
    business_name: str
    domain: str
    email: str


class OnboardResponse(BaseModel):
    client_id: str
    status: str


@app.post("/onboard", response_model=OnboardResponse)
async def onboard(req: OnboardRequest):
    client_id = uuid.uuid4().hex[:12]
    JOBS[client_id] = {
        "status": "running",
        "business_name": req.business_name,
        "domain": req.domain,
        "email": req.email,
        "started_at": time.time(),
        "report": None,
    }
    asyncio.create_task(run_profiling(client_id, req))
    return OnboardResponse(client_id=client_id, status="running")


@app.get("/onboard/status/{client_id}")
async def onboard_status(client_id: str):
    job = JOBS.get(client_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Unknown client_id")
    return job


@app.get("/health")
def health():
    return {"status": "ok"}


async def run_profiling(client_id: str, req: OnboardRequest):
    loop = asyncio.get_event_loop()
    try:
        usernames = derive_usernames(req.business_name, req.domain)
        sherlock_results = await loop.run_in_executor(None, run_sherlock, usernames)
        hunter_results = await loop.run_in_executor(None, run_hunter, req.domain)
        hibp_results = await loop.run_in_executor(None, run_hibp, req.email)

        JOBS[client_id]["report"] = {
            "sherlock": sherlock_results,
            "hunter": hunter_results,
            "hibp": hibp_results,
            "findings": build_findings(sherlock_results, hunter_results, hibp_results),
        }
        JOBS[client_id]["status"] = "complete"
    except Exception as exc:
        JOBS[client_id]["status"] = "failed"
        JOBS[client_id]["error"] = str(exc)


def derive_usernames(business_name: str, domain: str) -> list[str]:
    # Sherlock matches literal usernames, not free text - "Riverside Cafe"
    # matches nothing on any platform because real handles don't have
    # spaces. Derive plausible handles from what we actually have instead.
    candidates = []

    slug = re.sub(r"[^a-z0-9]", "", business_name.lower())
    if slug:
        candidates.append(slug)

    domain_root = re.sub(r"[^a-z0-9]", "", domain.lower().split(".")[0]) if domain else ""
    if domain_root and domain_root not in candidates:
        candidates.append(domain_root)

    return candidates or [business_name]


SHERLOCK_URL_RE = re.compile(r"https?://\S+")


def run_sherlock(usernames: list[str]) -> list[str]:
    if not usernames:
        return []
    try:
        result = subprocess.run(
            ["sherlock", *usernames, "--print-found", "--timeout", "10"],
            capture_output=True,
            text=True,
            timeout=180,
        )
        # Sherlock prints "[+] SiteName: https://..." per match, not a bare
        # URL - extract the URL from wherever it appears in the line.
        urls = []
        for line in result.stdout.splitlines():
            match = SHERLOCK_URL_RE.search(line)
            if match:
                urls.append(match.group(0))
        return urls
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []


def run_hunter(domain: str) -> dict:
    if not HUNTER_API_KEY:
        return {}
    resp = requests.get(
        "https://api.hunter.io/v2/domain-search",
        params={"domain": domain, "api_key": HUNTER_API_KEY},
        timeout=10,
    )
    return resp.json() if resp.ok else {}


def run_hibp(email: str) -> list[dict]:
    if not HIBP_API_KEY:
        return []
    resp = requests.get(
        f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
        headers={"hibp-api-key": HIBP_API_KEY},
        timeout=10,
    )
    return resp.json() if resp.status_code == 200 else []


def build_findings(sherlock_results: list[str], hunter_results: dict, hibp_results: list[dict]) -> dict:
    platforms = {}
    for platform, domain in PLATFORM_DOMAINS.items():
        matches = [url for url in sherlock_results if domain in url]
        platforms[platform] = {
            "signal_found": bool(matches),
            "evidence": [f"Profile found via username search: {url}" for url in matches],
            # QC's 2-of-3 rule needs 2+ independent sources before a claim
            # is shown to the client - one Sherlock match alone is a lead,
            # not a verified claim.
            "sources_verified": 1 if matches else 0,
        }

    domain_emails = hunter_results.get("data", {}).get("emails", []) if isinstance(hunter_results, dict) else []

    return {
        "platforms": platforms,
        "domain_contacts_found": len(domain_emails),
        "breach_count": len(hibp_results) if isinstance(hibp_results, list) else 0,
        "hunter_configured": bool(HUNTER_API_KEY),
        "hibp_configured": bool(HIBP_API_KEY),
    }
