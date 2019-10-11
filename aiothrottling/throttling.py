import asyncio
import re
from functools import wraps
from time import time


class Throttle:
    """
    Rate throttling of coroutine calls.

    Instance of this class is awaitable object.
    """

    PERIOD = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    RATE_MASK = re.compile(r'([0-9]*)([A-Za-z]+)')

    @property
    def rate(self):
        return '{limit}/{period}'.format(limit=self.limit, period=self.period)

    @rate.setter
    def rate(self, value):
        num, period = value.split('/')
        self.limit = int(num)
        factor, base = self.RATE_MASK.match(period).groups()
        self.period = (int(factor or 1)) * self.PERIOD[base[0].lower()]

    __slots__ = ('history', 'limit', 'period')

    def __init__(self, rate):
        self.history = []
        self.rate = rate

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


throttle = Throttle
