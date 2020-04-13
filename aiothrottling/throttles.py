"""Rate limiting primitives."""

__all__ = [
    'DistributedThrottle', 'LockingThrottle', 'dthrottle'
]

import asyncio
import random
from collections import deque
from time import time

from aiothrottles.throttles import RateMixin, Throttle

from .lock import Lock


class LockingThrottle(RateMixin):
    """Abstract throttle that can lock resources."""

    __slots__ = ('resources', 'lock')

    def __init__(self, resources, rate='3/s', lock=None):
        super().__init__(rate)
        self.resources = resources
        self.lock = lock or Lock()

    async def __aenter__(self):
        for res in self.resources:
            await self.lock.acquire(self.pk(res))

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for res in self.resources:
            self.lock.release(self.pk(res))

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
