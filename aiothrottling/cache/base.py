"""Module with abstract cache."""


class Cache:
    """Simple cache interface."""

    async def check_in(self, *args):
        pass

    async def check(self, *args):
        pass

    async def check_out(self, *args):
        pass


class MemoryCache(Cache):
    """Cache that checks in smth as a couple of (key, digest)."""

    __slots__ = ('memory', )

    def __init__(self):
        self.memory = {}

    async def check_in(self, pk, digest):
        self.memory[pk] = digest

    async def check(self, pk):
        return self.memory.get(pk)

    async def check_out(self, pk):
        if pk in self.memory:
            del self.memory[pk]
