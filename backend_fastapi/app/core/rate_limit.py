import asyncio
import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import Request

from app.core.custom_exceptions import RateLimitException


class SimpleRateLimiter:
    def __init__(self) -> None:
        self._events: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def hit(self, key: str, limit: int, window_seconds: int) -> None:
        now = time.time()
        async with self._lock:
            bucket = self._events[key]
            cutoff = now - window_seconds
            while bucket and bucket[0] < cutoff:
                bucket.popleft()
            if len(bucket) >= limit:
                retry_after = (
                    int(bucket[0] + window_seconds - now) if bucket else window_seconds
                )
                raise RateLimitException(details={"retry_after": max(0, retry_after)})
            bucket.append(now)


limiter = SimpleRateLimiter()


async def enforce_rate_limit(
    request: Request, key: str, limit: int, window_seconds: int
) -> None:
    client_ip = request.client.host if request.client else "unknown"
    await limiter.hit(f"{key}:{client_ip}", limit, window_seconds)
