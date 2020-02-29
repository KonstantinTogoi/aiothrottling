"""Rate limiting primitives."""

__all__ = [
    'Throttle', 'DistributedThrottle', 'LockingThrottle',
    'throttle', 'dthrottle'
]

import asyncio
import collections
import random
import re
from collections import deque
from functools import wraps
from time import time

from .lock import Lock


class ThrottleMixin:
    """Encapsulates rate."""

    PERIOD = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    RATE_MASK = re.compile(r'([0-9]*)([A-Za-z]+)')

    @property
    def rate(self):
        return '{limit}/{period}'.format(limit=self.limit, period=self.period)

    @rate.setter
    def rate(self, value):
        num, period = value.split('/')
        factor, base = self.RATE_MASK.match(period).groups()
        self.limit = int(num)
        self.period = (int(factor or 1)) * self.PERIOD[base[0].lower()]

    __slots__ = ('limit', 'period')

    def __init__(self, rate):
        self.rate = rate

    def __call__(self, coro):
        @wraps(coro)
        async def wrapper(*args, **kwargs):
            async with self:
                return await coro(*args, **kwargs)
        return wrapper

    def __await__(self):
        return self.acquire().__await__()

    async def __aenter__(self):
        await self.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release()

    async def acquire(self):
        pass

    def release(self):
        pass


class Throttle(ThrottleMixin):
    """
    Rate throttling of coroutine calls.

    Instance of this class is awaitable object.
    """

    __slots__ = ('_loop', '_waiters', '_trace')

    def __init__(self, rate, *, loop=None):
        super().__init__(rate)
        self._loop = loop or asyncio.get_event_loop()
        self._waiters = collections.deque()
        self._trace = collections.deque()

    def locked(self):
        """Return True if throttle was acquired
        more than `limit` times during the `period`."""
        now = time()
        while self._trace and now - self._trace[0] > self.period:
            self._trace.popleft()
        return len(self._trace) >= self.limit

    async def acquire(self):
        """Acquire a throttle."""
        fut = self._loop.create_future()
        self._waiters.append(fut)
        while True:
            if fut.done():
                self._waiters.remove(fut)
                break
            elif self.locked():
                delay = self.period - (time() - self._trace[0])
                await asyncio.sleep(delay)
            else:
                for fut in self._waiters:
                    if not fut.done():
                        fut.set_result(True)

    def release(self):
        """Release a throttle."""
        self._trace.append(time())


class LockingThrottle(ThrottleMixin):
    """Abstract throttle that can lock resources."""

    __slots__ = ('resources', 'lock')

    def __init__(self, resources, rate='3/s', lock: Lock = None):
        super().__init__(rate)
        self.resources = resources
        self.lock = lock

    async def __aenter__(self):
        if self.lock:
            for res in self.resources:
                await self.lock.acquire(self.pk(res))

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.lock:
            for res in self.resources:
                await self.lock.release(self.pk(res))

    def pk(self, resource):
        """A resource's key for lock table."""
        ix = self.resources.index(resource)
        return bytes(ix)


class DistributedThrottle(LockingThrottle):
    """Distributed throttle."""

    NO_RESOURCES_ERROR = RuntimeError('no resources available')

    @property
    def n_resources(self):
        return len(self.resources)

    __slots__ = ('shuffle', 'histories', 'blocked', 'vacant_num')

    def __init__(self, resources, rate='3/s', lock=None, shuffle=False):
        super().__init__(resources, rate=rate, lock=lock)
        self.shuffle = shuffle
        self.histories = [(i, deque()) for i in range(len(resources))]
        self.blocked = []
        self.vacant_num = -1

    async def __aenter__(self):
        return await self.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def block(self, resource):
        """Marks a resource as invalid / unavailable."""
        ix = self.resources.index(resource)
        self.blocked.append(ix)

    def flush(self, now):
        """Cleans resources' histories."""
        for i, history in self.histories:
            while history and now - history[0] > self.period:
                history.popleft()

    async def acquire(self, num=None):
        """Returns available resource."""
        histories = self.histories if num is None else [self.histories[num]]
        histories = [(i, h) for i, h in histories if i not in self.blocked]

        if len(histories) == 0:
            raise self.NO_RESOURCES_ERROR

        if self.shuffle:
            random.shuffle(histories)

        vacant_num = None

        while True:
            now = time()
            self.flush(now)

            for i, history in histories:
                if len(history) < self.limit:
                    vacant_num = i
                    break

            if vacant_num is not None:
                break
            else:
                delay = self.period - (now - min(h[0] for h in histories))
                await asyncio.sleep(delay)

        self.vacant_num = vacant_num
        return self.resources[vacant_num]

    def release(self):
        self.histories[self.vacant_num][1].append(time())


throttle = Throttle
dthrottle = DistributedThrottle
