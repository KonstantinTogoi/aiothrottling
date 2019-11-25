from time import time

import pytest

from aiothrottling import Throttle, DistributedThrottle


class TestThrottle:

    NUM_ITERS = 10

    @pytest.fixture(params=['3/s', '6/s', '8/2s', '9/3s'])
    def rate(self, request):
        return request.param

    @pytest.fixture
    def throttle(self, rate):
        return Throttle(rate=rate)

    @pytest.mark.asyncio
    async def test_decorator(self, throttle):
        interval = throttle.period / throttle.limit
        now = time() - interval

        @throttle
        async def foo():
            pass

        for i in range(self.NUM_ITERS):
            await foo()
            if i % throttle.limit == 0:
                assert time() - now >= interval
                now = time()

    @pytest.mark.asyncio
    async def test_awaitable(self, throttle):
        interval = throttle.period / throttle.limit
        now = time() - interval

        for i in range(self.NUM_ITERS):
            await throttle
            if i % throttle.limit == 0:
                assert time() - now >= interval
                now = time()

    @pytest.mark.asyncio
    async def test_context(self, throttle):
        interval = throttle.period / throttle.limit
        now = time() - interval

        for i in range(self.NUM_ITERS):
            async with throttle:
                if i % throttle.limit == 0:
                    assert time() - now >= interval
                    now = time()


class TestDistributedThrottle:

    @pytest.fixture(params=['3/s', '6/s', '8/2s', '9/3s'])
    def rate(self, request):
        return request.param

    @pytest.fixture
    @pytest.mark.asyncio
    async def throttle(self, resources, rate):
        return DistributedThrottle(resources, rate=rate)

    @pytest.fixture
    @pytest.mark.asyncio
    async def shuffled_throttle(self, resources, rate):
        return DistributedThrottle(resources, rate=rate, shuffle=True)

    @pytest.mark.asyncio
    async def test_acquire(self, throttle):
        await self._test_acquire(throttle)

    @pytest.mark.asyncio
    async def test_acquire_with_shuffle(self, shuffled_throttle):
        await self._test_acquire(shuffled_throttle)

    @staticmethod
    async def _test_acquire(throttle):
        n_resources = len(throttle.resources)
        interval = throttle.period / throttle.limit / n_resources

        names = []
        for i in range(len(throttle.resources) * 3):
            last_time = 0
            async with throttle.acquire() as resource:
                current_time = time()
                assert (current_time - last_time) > interval
                names.append(resource.name)
