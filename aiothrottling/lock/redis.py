from .base import ExclusiveCacheLock
from ..cache.redis import RedisCache


class RedisLock(RedisCache, ExclusiveCacheLock):
    """Redis-based lock."""

    def __init__(self, conn=None, hash_name='locked', retry_interval=1):
        RedisCache.__init__(self, conn, hash_name)
        ExclusiveCacheLock.__init__(self, retry_interval)

    async def acquire(self, pk: bytes, digest: bytes = b'1'):
        return await super().acquire(pk, digest)
