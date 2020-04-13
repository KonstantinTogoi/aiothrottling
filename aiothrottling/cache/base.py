"""Module with abstract cache."""


class Cache:
    """Simple interface of a cache that checks in couples (key, value)."""

    def check_in(self, key, value):
        pass

    def check(self, key):
        pass

    def check_out(self, key):
        pass


class MemoryCache(Cache):
    """Cache that uses memory to check in."""

    __slots__ = ('memory', )

    def __init__(self):
        self.memory = {}

    def check_in(self, key, value):
        self.memory[key] = value

    def check(self, key):
        return self.memory.get(key)

    def check_out(self, key):
        if key in self.memory:
            del self.memory[key]
