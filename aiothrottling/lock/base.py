"""Module with abstract lock."""
import asyncio

from ..cache import Cache


class Lock:
    """Simple lock interface."""

    async def acquire(self, *args):
        pass

    async def release(self, *args):
        pass


class CacheLock(Lock, Cache):
    """Lock that uses cache."""

    async def acquire(self, *args):
        return self.check_in(*args)

    async def release(self, *args):
        return self.check_out(*args)


class ExclusiveCacheLock(Cache):
    """Lock that uses cache with exclusive keys."""

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
