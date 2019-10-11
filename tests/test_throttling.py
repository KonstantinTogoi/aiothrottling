from time import time

import pytest

from aiothrottling import Throttle


class TestThrottle:

    @pytest.fixture(params=['3/s', '6/s', '8/2s', '9/3s'])
    def throttle(self, request):
        return Throttle(request.param)

    @pytest.mark.asyncio
    async def test_rate(self, throttle):
        interval = throttle.period / throttle.limit
        now = time() - interval

        for i in range(5):
            await throttle
            if i % throttle.limit == 0:
                assert time() - now >= interval
                now = time()
