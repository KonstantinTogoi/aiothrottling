"""Module with locks for resources."""


class BaseLock:
    """Base resources lock."""

    __slots__ = ()

    async def acquire(self, pk: bytes):
        pass

    async def release(self, pk: bytes):
        pass
