"""Module with abstract lock."""
import asyncio

from ..cache import Cache


class Lock(Cache):
    """Abstract resources lock."""

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
