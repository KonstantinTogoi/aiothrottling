from time import time

import pytest

from aiothrottling import Throttle, DistributedThrottle
from aiothrottling.lock import MemoryLock


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

    @pytest.fixture
    @pytest.mark.asyncio
    async def locking_throttle(self, resources, rate):
        return DistributedThrottle(resources, rate=rate, lock=MemoryLock())

    @pytest.mark.asyncio
    async def test_acquire(self, throttle):
        await self._test_acquire(throttle)

    @pytest.mark.asyncio
    async def test_acquire_with_shuffle(self, shuffled_throttle):
        await self._test_acquire(shuffled_throttle)

    @pytest.mark.asyncio
    async def test_acquire_with_locking(self, locking_throttle):
        await self._test_acquire(locking_throttle)

    @staticmethod
    async def _test_acquire(throttle):
        max_n_calls = throttle.limit * len(throttle.resources)

        start_time = time()
        for i in range(max_n_calls):
            async with throttle:
                pass
        stop_time = time()

        assert stop_time - start_time <= throttle.period

        async with throttle:
            pass

        assert time() - start_time > throttle.period
