import asyncio
import os
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
        sherlock_results = await loop.run_in_executor(None, run_sherlock, req.business_name)
        hunter_results = await loop.run_in_executor(None, run_hunter, req.domain)
        hibp_results = await loop.run_in_executor(None, run_hibp, req.email)

        JOBS[client_id]["report"] = {
            "sherlock": sherlock_results,
            "hunter": hunter_results,
            "hibp": hibp_results,
        }
        JOBS[client_id]["status"] = "complete"
    except Exception as exc:
        JOBS[client_id]["status"] = "failed"
        JOBS[client_id]["error"] = str(exc)


def run_sherlock(username: str) -> list[str]:
    try:
        result = subprocess.run(
            ["sherlock", username, "--print-found", "--timeout", "10"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        return [line for line in result.stdout.splitlines() if line.startswith("http")]
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
