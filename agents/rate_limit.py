import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, min_interval: float = 3.0):
        super().__init__(app)
        self.min_interval = min_interval
        self._last_seen: dict[str, float] = defaultdict(float)

    async def dispatch(self, request, call_next):
        # Only throttle mutating requests (onboarding trigger, cookie
        # submission) - GET status/health checks aren't what the "max 1
        # req/3sec" constraint is protecting against, and a single
        # dashboard page load legitimately fires several of them at once
        # (platform status + report status concurrently). Rate-limiting
        # those too made every dashboard load flaky: one of the two
        # concurrent GETs would 429 and render as "not connected"/"no
        # profile found" even when the data was there.
        if request.method == "GET":
            return await call_next(request)

        ip = request.client.host if request.client else "unknown"
        now = time.monotonic()
        elapsed = now - self._last_seen[ip]
        if elapsed < self.min_interval:
            return JSONResponse(
                {"detail": "Rate limit exceeded, max 1 request per 3 seconds"},
                status_code=429,
            )
        self._last_seen[ip] = now
        return await call_next(request)
