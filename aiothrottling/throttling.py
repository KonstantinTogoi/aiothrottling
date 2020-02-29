import asyncio
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


class Throttle(ThrottleMixin):
    """
    Rate throttling of coroutine calls.

    Instance of this class is awaitable object.
    """

    __slots__ = ('history', )

    def __init__(self, rate):
        super().__init__(rate)
        self.history = []

    def __call__(self, coro):
        @wraps(coro)
        async def wrapper(*args, **kwargs):
            await self.delay()
            return await coro(*args, **kwargs)
        return wrapper

    def __await__(self):
        return self.delay().__await__()

    async def __aenter__(self):
        await self.delay()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    async def delay(self):
        while True:
            now = time()
            while self.history and now - self.history[-1] > self.period:
                self.history.pop()

            if len(self.history) < self.limit:
                self.history.insert(0, now)
                break
            else:
                delay = self.period - (now - self.history[-1])
                await asyncio.sleep(delay)


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
