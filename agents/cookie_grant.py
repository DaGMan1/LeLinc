import json
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agents.rate_limit import RateLimitMiddleware

COOKIES_ROOT = Path("/cookies")

# Same platform set as agents/orchestrator.py's PLATFORM_DOMAINS - kept as
# a separate small constant here rather than a shared import, since it's
# four strings and not worth a cross-module dependency for.
PLATFORM_DOMAINS = {
    "instagram": "instagram.com",
    "linkedin": "linkedin.com",
    "facebook": "facebook.com",
    "tiktok": "tiktok.com",
}

app = FastAPI(title="LeLinc Cookie Grant")
app.add_middleware(RateLimitMiddleware, min_interval=3.0)


class CookieGrantRequest(BaseModel):
    client_id: str
    platform: str
    cookies: str
    expires_at: float | None = None


class CookieImportRequest(BaseModel):
    client_id: str
    platform: str
    cookies_txt: str


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


def parse_netscape_cookies(text: str, domain_filter: str) -> list[dict]:
    """Parse a Netscape/Mozilla cookie file (what 'Get cookies.txt' and
    similar exporters produce) and return only cookies matching domain_filter.

    Format: 7 tab-separated fields per line - domain, includeSubdomains,
    path, secure, expiry, name, value. A '#HttpOnly_' prefix on the domain
    field (the curl/wget convention most exporters follow) marks httpOnly
    cookies, which is exactly the class of cookie we need (session tokens
    are httpOnly precisely so page JS can't read them).
    """
    cookies = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        http_only = line.startswith("#HttpOnly_")
        if http_only:
            line = line[len("#HttpOnly_"):]
        elif line.startswith("#"):
            continue

        parts = line.split("\t")
        if len(parts) != 7:
            continue
        domain, _include_sub, path, secure, expiry, name, value = parts
        if domain_filter not in domain:
            continue

        cookies.append(
            {
                "name": name,
                "value": value,
                "domain": domain,
                "path": path,
                "secure": secure.upper() == "TRUE",
                "httpOnly": http_only,
                "expirationDate": float(expiry) if expiry.replace(".", "", 1).isdigit() else None,
            }
        )
    return cookies


@app.post("/cookies/import")
def import_cookies(req: CookieImportRequest):
    domain_filter = PLATFORM_DOMAINS.get(req.platform.lower())
    if domain_filter is None:
        raise HTTPException(status_code=400, detail=f"Unknown platform: {req.platform}")

    cookies = parse_netscape_cookies(req.cookies_txt, domain_filter)
    if not cookies:
        raise HTTPException(
            status_code=422,
            detail=f"No {req.platform} cookies found in that file - make sure you exported "
            f"after logging in, and on a {domain_filter} tab.",
        )

    expires_at = max((c["expirationDate"] for c in cookies if c["expirationDate"]), default=None)

    client_dir = COOKIES_ROOT / req.client_id
    client_dir.mkdir(parents=True, exist_ok=True)
    record = {
        "platform": req.platform,
        "cookies": json.dumps(cookies),
        "granted_at": time.time(),
        "expires_at": expires_at,
    }
    (client_dir / f"{req.platform}.json").write_text(json.dumps(record))
    return {"status": "stored", "platform": req.platform, "cookie_count": len(cookies)}


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
