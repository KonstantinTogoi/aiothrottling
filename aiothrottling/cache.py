"""Module with cache definitions."""
from redis import ConnectionPool, Redis


class Cache:
    """Simple cache interface."""

    async def check_in(self, pk, digest):
        raise NotImplementedError()

    async def check(self, pk):
        raise NotImplementedError()

    async def check_out(self, pk):
        raise NotImplementedError()


class RedisCache(Cache):
    """Redis-based cache."""

    _cache = None

    @property
    def cache(self):
        if self._cache is None:
            self._cache = Redis(connection_pool=ConnectionPool(**self.conn))
        return self._cache

    __slots__ = ('conn', 'hash_name')

    def __init__(self, conn=None, hash_name='locked'):
        super().__init__()
        self.conn = conn or {}
        self.hash_name = hash_name

    async def check_in(self, pk: bytes, digest: bytes = b'1'):
        return self.cache.hmset(self.hash_name, {pk: digest})

    async def check(self, pk: bytes):
        return self.cache.hget(self.hash_name, pk)

    async def check_out(self, pk: bytes):
        return self.cache.hdel(self.hash_name, pk)
