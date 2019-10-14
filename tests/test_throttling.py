from time import time

import pytest

from aiothrottling import Throttle


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
