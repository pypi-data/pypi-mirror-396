"""
Rate-limited semaphore for controlling concurrent operations.
"""

import asyncio
import time


class RateLimitSemaphore(asyncio.Semaphore):
    """
    A semaphore that limits both the maximum number of concurrent acquisitions
    and the maximum rate at which acquisitions can occur.
    """

    @property
    def max_concurrent(self) -> int:
        """Maximum number of concurrent acquisitions."""
        return self._max_concurrent

    @property
    def max_per_second(self) -> float:
        """Maximum acquisitions per second."""
        return self._max_per_second

    def __init__(self, max_concurrent: int, max_per_second: float):
        """
        Initialize the rate-limited semaphore.

        Args:
            max_concurrent: Maximum number of concurrent acquisitions.
            max_per_second: Maximum acquisitions per second.
        """
        super().__init__(max_concurrent)
        self._max_concurrent = max_concurrent
        self._max_per_second = max_per_second

        self._acquire_interval = 1.0 / max_per_second
        self._next_acquire_time = 0
        self._rate_lock = asyncio.Lock()

    async def acquire(self):
        """
        Acquire a semaphore with rate limiting.

        In addition to traditional semaphore behavior, this will also rate limit
        the number of acquisitions per second by blocking until the next
        acquisition interval.
        """
        # Rate limit acquisitions (serialized to prevent race conditions)
        async with self._rate_lock:
            now = time.monotonic()
            wait = self._next_acquire_time - now

            if wait > 0:
                # Sleep until next acquisition interval
                await asyncio.sleep(wait)
                self._next_acquire_time += self._acquire_interval

            else:
                # no wait, set next acquisition time to next interval
                self._next_acquire_time = now + self._acquire_interval

        # Acquire semaphore for concurrency limiting
        return await super().acquire()
