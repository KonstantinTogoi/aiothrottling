"""Module with locks for resources."""
import asyncio
import logging

import redis

log = logging.getLogger(__name__)


class BaseLock:
    """Base resources lock."""

    __slots__ = ()

    async def acquire(self, pk: bytes):
        raise NotImplementedError()

    async def release(self, pk: bytes):
        raise NotImplementedError()


class RedisLock(BaseLock):

    INTERVAL = 15

    def __init__(self, conn=None, hash_name='locked', verbose=False):
        self.conn = conn or {}
        self.cache = None
        self.hash_name = hash_name
        self.verbose = verbose

    async def init(self):
        if self.cache is None:
            pool = redis.ConnectionPool(**self.conn)
            self.cache = redis.Redis(connection_pool=pool)

    async def acquire(self, pk: bytes):
        if self.verbose:
            log.info('locking in {}'.format(pk))
        while self.check(pk):
            if self.verbose:
                log.info('resource with pk {} is locked'.format(pk))
            await asyncio.sleep(self.INTERVAL)
        else:
            self.check_in(pk, b'1')

    async def release(self, pk: bytes):
        if self.verbose:
            log.info('releasing {}'.format(pk))

    def check_in(self, pk: bytes, digest: bytes):
        if self.verbose:
            log.info('checking in a digest with pk = {}'.format(pk))
        self.cache.hmset(self.hash_name, {pk: digest})

    def check(self, pk: bytes):
        if self.verbose:
            log.info('checking a digest with pk = {}'.format(pk))
        return self.cache.hget(self.hash_name, pk)

    def check_out(self, pk: bytes):
        if self.verbose:
            log.info('checking out a digest with pk = {}'.format(pk))
        self.cache.hdel(self.hash_name, pk)
