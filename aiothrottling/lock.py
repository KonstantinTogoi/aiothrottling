"""Module with locks for resources."""
import asyncio
import logging

import redis

log = logging.getLogger(__name__)


class Lock:
    """Base resources lock."""

    __slots__ = ('retry_interval', )

    def __init__(self, retry_interval=1):
        self.retry_interval = retry_interval

    async def acquire(self, pk):
        while await self.check(pk):
            await asyncio.sleep(self.retry_interval)
        else:
            await self.check_in(pk)

    async def release(self, pk):
        await self.check_out(pk)

    async def check_in(self, pk, digest=b'1'):
        raise NotImplementedError()

    async def check(self, pk):
        raise NotImplementedError()

    async def check_out(self, pk):
        raise NotImplementedError()


class RedisLock(Lock):

    def __init__(self, conn=None, hash_name='locked'):
        super().__init__()
        self.conn = conn or {}
        self.cache = None
        self.hash_name = hash_name

    async def init(self):
        if self.cache is None:
            pool = redis.ConnectionPool(**self.conn)
            self.cache = redis.Redis(connection_pool=pool)

    async def check_in(self, pk: bytes, digest: bytes = b'1'):
        self.cache.hmset(self.hash_name, {pk: digest})

    async def check(self, pk: bytes):
        return self.cache.hget(self.hash_name, pk)

    async def check_out(self, pk: bytes):
        self.cache.hdel(self.hash_name, pk)
