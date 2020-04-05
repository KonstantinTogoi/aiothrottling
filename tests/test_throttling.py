from time import time

import pytest

from aiothrottling import DistributedThrottle
from aiothrottling.lock import MemoryLock


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
        max_n_calls = throttle.limit.numerator * len(throttle.resources)

        start_time = time()
        for i in range(max_n_calls):
            async with throttle:
                pass
        stop_time = time()

        assert stop_time - start_time <= throttle.period

        async with throttle:
            pass

        assert time() - start_time > throttle.period
