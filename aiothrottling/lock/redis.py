from ..lock import Lock
from ..cache.redis import RedisCache


class RedisLock(RedisCache, Lock):
    """Redis-based lock."""

    def __init__(self, conn=None, hash_name='locked'):
        super().__init__(conn, hash_name)

    async def acquire(self, pk: bytes, digest: bytes = b'1'):
        return await super().acquire(pk, digest)
