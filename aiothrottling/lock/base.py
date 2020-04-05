"""Module with abstract lock."""
import asyncio

from ..cache import Cache, MemoryCache


class Lock:
    """Simple lock interface."""

    async def acquire(self, *args):
        pass

    async def release(self, *args):
        pass


class CacheLock(Lock, Cache):
    """Lock that uses cache."""

    async def acquire(self, key, value):
        return self.check_in(key, value)

    async def release(self, key):
        return self.check_out(key)


class ExclusiveLock(Cache):
    """Lock that uses cache with exclusive keys."""

    def __init__(self, retry_interval=1):
        self.retry_interval = retry_interval

    async def acquire(self, key, value):
        while await self.check(key):
            await asyncio.sleep(self.retry_interval)
        else:
            await self.check_in(key, value)

    async def release(self, key):
        await self.check_out(key)


class MemoryLock(MemoryCache, ExclusiveLock):
    """Lock that uses memory for locking."""
