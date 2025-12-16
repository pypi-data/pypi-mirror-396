"""
Utility helpers: RateLimiter and ExponentialBackoff used by the client.

These are intentionally dependency-free helpers that are easy to test
and replace with more sophisticated implementations if desired.
"""
import time
from typing import Dict, List, Optional


class RateLimiter:
    """A simple in-memory sliding-window rate limiter keyed by id.

    Not persistent; suitable for single-process server usage.
    
    Example:
        limiter = RateLimiter(max_attempts=10, window_minutes=1)
        if limiter.is_allowed('api_key'):
            # make request
            pass
        else:
            retry_after = limiter.get_retry_after('api_key')
    """

    def __init__(self, max_attempts: int = 10, window_minutes: int = 1):
        self.max_attempts = max_attempts
        self.window_seconds = window_minutes * 60
        self._buckets: Dict[str, List[float]] = {}

    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed for the given key."""
        now = time.time()
        window_start = now - self.window_seconds
        bucket = self._buckets.setdefault(key, [])
        # purge old timestamps
        while bucket and bucket[0] < window_start:
            bucket.pop(0)
        if len(bucket) < self.max_attempts:
            bucket.append(now)
            return True
        return False

    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        self._buckets.pop(key, None)

    def get_retry_after(self, key: str) -> float:
        """Return seconds until next attempt allowed for key or 0.0 if allowed now."""
        now = time.time()
        bucket = self._buckets.get(key, [])
        if len(bucket) < self.max_attempts:
            return 0.0
        oldest = bucket[0]
        retry_at = oldest + self.window_seconds
        return max(0.0, retry_at - now)


class ExponentialBackoff:
    """Simple exponential backoff helper for retries.
    
    Example:
        backoff = ExponentialBackoff(base_delay=1.0, max_delay=60.0)
        for attempt in range(5):
            try:
                # make request
                break
            except Exception:
                delay = backoff.get_delay(attempt)
                time.sleep(delay)
    """

    def __init__(self, base_delay: float = 1.0, max_delay: float = 60.0, multiplier: float = 2.0):
        self.base_delay = float(base_delay)
        self.max_delay = float(max_delay)
        self.multiplier = float(multiplier)

    def get_delay(self, attempt: int) -> float:
        """Get delay in seconds for the given attempt number."""
        delay = self.base_delay * (self.multiplier ** attempt)
        return min(delay, self.max_delay)

    def sleep(self, attempt: int) -> None:
        """Sleep for the appropriate delay based on attempt number."""
        delay = self.get_delay(attempt)
        time.sleep(delay)
