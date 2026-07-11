import json
import time
from pathlib import Path

from fastapi import FastAPI
from pydantic import BaseModel

from agents.rate_limit import RateLimitMiddleware

COOKIES_ROOT = Path("/cookies")

app = FastAPI(title="LeLinc Cookie Grant")
app.add_middleware(RateLimitMiddleware, min_interval=3.0)


class CookieGrantRequest(BaseModel):
    client_id: str
    platform: str
    cookies: str
    expires_at: float | None = None


class PlatformStatus(BaseModel):
    platform: str
    connected: bool
    granted_at: float | None = None
    expires_at: float | None = None
    expired: bool = False


@app.post("/cookies")
def grant_cookies(req: CookieGrantRequest):
    client_dir = COOKIES_ROOT / req.client_id
    client_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "platform": req.platform,
        "cookies": req.cookies,
        "granted_at": time.time(),
        "expires_at": req.expires_at,
    }
    (client_dir / f"{req.platform}.json").write_text(json.dumps(record))
    return {"status": "stored", "platform": req.platform}


@app.get("/cookies/status/{client_id}", response_model=list[PlatformStatus])
def cookie_status(client_id: str):
    client_dir = COOKIES_ROOT / client_id
    if not client_dir.exists():
        return []
    now = time.time()
    statuses = []
    for f in sorted(client_dir.glob("*.json")):
        record = json.loads(f.read_text())
        expires_at = record.get("expires_at")
        statuses.append(
            PlatformStatus(
                platform=record["platform"],
                connected=True,
                granted_at=record.get("granted_at"),
                expires_at=expires_at,
                expired=bool(expires_at and expires_at < now),
            )
        )
    return statuses


@app.get("/health")
def health():
    return {"status": "ok"}
