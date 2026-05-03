import asyncio
import time
from collections import defaultdict, deque

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_per_minute: int = 120):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60
        self.buckets: dict[str, deque[float]] = defaultdict(deque)
        self.lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next):
        key = request.client.host if request.client else "unknown"
        now = time.time()
        async with self.lock:
            bucket = self.buckets[key]
            while bucket and now - bucket[0] > self.window_seconds:
                bucket.popleft()
            if len(bucket) >= self.requests_per_minute:
                return JSONResponse({"detail": "Rate limit exceeded"}, status_code=429)
            bucket.append(now)
        return await call_next(request)


def add_rate_limiting(app) -> None:  # type: ignore[no-untyped-def]
    app.add_middleware(RateLimitMiddleware, requests_per_minute=240)
