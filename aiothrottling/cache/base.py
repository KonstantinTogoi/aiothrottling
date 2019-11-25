"""Module with abstract cache."""


class Cache:
    """Simple cache interface."""

    async def check_in(self, pk, digest):
        pass

    async def check(self, pk):
        pass

    async def check_out(self, pk):
        pass
