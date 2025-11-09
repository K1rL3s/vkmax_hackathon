import asyncio
import collections
import functools
import time
from collections.abc import Awaitable, Callable
from types import TracebackType
from typing import Any, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


class RateLimiter:
    def __init__(self, max_calls: int, period: float = 1.0) -> None:
        if period <= 0:
            raise ValueError("Rate limiting period should be > 0")
        if max_calls <= 0:
            raise ValueError("Rate limiting number of calls should be > 0")

        self.calls: collections.deque[float] = collections.deque()

        self.period = period
        self.max_calls = max_calls

        self._lock = asyncio.Lock()

    def __call__(self, f: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(f)
        async def wrapped(*args: P.args, **kwargs: P.kwargs) -> Any:
            async with self:
                return await f(*args, **kwargs)

        return wrapped

    async def __aenter__(self) -> "RateLimiter":
        while True:
            async with self._lock:
                current = time.time()
                while self.calls and current - self.calls[0] >= self.period:
                    self.calls.popleft()
                if len(self.calls) < self.max_calls:
                    self.calls.append(current)
                    return self
                until = self.calls[0] + self.period
                sleeptime = until - current
            await asyncio.sleep(max(0.0, sleeptime))

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        pass
