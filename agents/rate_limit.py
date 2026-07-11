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
