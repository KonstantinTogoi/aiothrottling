"""Module with abstract lock."""
import asyncio

from ..cache import Cache


class Lock:
    """Abstract resources lock."""

    async def acquire(self, *args):
        pass

    async def release(self, *args):
        pass


class CacheLock(Cache):
    """Lock that checks in a smth as a couple of (key, digest)."""

    __slots__ = ('retry_interval', )

    def __init__(self, retry_interval=1):
        self.retry_interval = retry_interval

    async def acquire(self, pk, digest):
        while await self.check(pk):
            await asyncio.sleep(self.retry_interval)
        else:
            await self.check_in(pk, digest)

    async def release(self, pk):
        await self.check_out(pk)
