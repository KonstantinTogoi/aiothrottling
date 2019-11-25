"""Module with locks for resources."""
import asyncio

from .cache import Cache, RedisCache


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


class RedisLock(RedisCache, Lock):
    """Redis-based lock."""

    def __init__(self, conn=None, hash_name='locked'):
        super().__init__(conn, hash_name)

    async def acquire(self, pk: bytes, digest: bytes = b'1'):
        return await super().acquire(pk, digest)
