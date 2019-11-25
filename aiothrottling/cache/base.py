"""Module with abstract cache."""


class Cache:
    """Simple interface of a cache that checks in couples (key, value)."""

    async def check_in(self, key, value):
        pass

    async def check(self, key):
        pass

    async def check_out(self, key):
        pass


class MemoryCache(Cache):
    """Cache that uses memory to check in."""

    __slots__ = ('memory', )

    def __init__(self):
        self.memory = {}

    async def check_in(self, key, value):
        self.memory[key] = value

    async def check(self, key):
        return self.memory.get(key)

    async def check_out(self, key):
        if key in self.memory:
            del self.memory[key]
