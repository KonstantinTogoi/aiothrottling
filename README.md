# aiothrottling

[![PyPI](https://img.shields.io/pypi/v/aiothrottling.svg)](https://pypi.python.org/pypi/aiothrottling)
[![PyPI version](https://img.shields.io/pypi/pyversions/aiothrottling.svg)](https://pypi.python.org/pypi/aiothrottling)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://aiothrottling.readthedocs.io/en/latest/)
[![Travis status](https://travis-ci.org/KonstantinTogoi/aiothrottling.svg)](https://travis-ci.org/KonstantinTogoi/aiothrottling)

*aiothrottling* synchronization primitives are designed to be extensions
(along the time) to *asyncio*'s synchronization primitives.

*aiothrottling* has the following basic synchronization primitives:

- `Throttle`

## Getting started

aiothrottling requires python 3.5+. Install package using pip

```python
pip install aiothrottling
```

### Throttle

Implements a rate limiting for asyncio task.
A throttle can be used to guarantee exclusive access to a shared resources
and locks access for a given time after releasing.

The preferred way to use a `Throttle` is an `async with` statement:

```python
throttle = Throttle('1/s')

# ... later
async with throttle:
    # access shared state
```

which is equivalent to:

```python
throttle  = Throttle('1/s')

# ... later
await throttle.acquire()
try:
    # access shared state
finally:
    throttle.release()
```

## Examples

### rates

The allowed coroutine call rate is determined by the ``rate`` argument. Pass the rate in the format `{limit}/{base period name}` or `{limit}/{factor}{base period name}`, for example

- full period name
    + `1/second`, `2/minute`, `3/hour`, `4/day`
- short period name
    + `4/s`, `5/m`, `6/h`, `7/d`
- set custom period by using a factor
    + `1/3s`, `12/37m`, `1/5h`, `8/3d`

### decorator

Use of `aiothrottling.Throttle` as decorator for coroutines:

```python
from aiothrottling import throttle  # Throttle alias
import time

@throttle(rate='1/s')
async def foo(n):
    print(n, time.time())

for i in range(5):
    await foo(i)

# 0 1563272100.4413373
# 1 1563272101.4427333
# 2 1563272102.4441307
# 3 1563272103.445542
# 4 1563272104.4468124
```

### awaitable

Use of `aiothrottling.Throttle` as awaitable object:

```python
from aiothrottling import Throttle
import time

throttle = Throttle(rate='1/s')

async def foo(n):
    print(n, time.time())

for i in range(5):
    await throttle
    await foo(i)

# 0 1563275828.253736
# 1 1563275829.2547996
# 2 1563275830.2562528
# 3 1563275831.257302
# 4 1563275832.2587304
```

### context manager

Use of `aiothrottling.Throttle` as context:

```python
from aiothrottling import Throttle
import time

throttle = Throttle(rate='1/s')

async def foo(n):
    print(n, time.time())

for i in range(5):
    async with throttle:
        await foo(i)

# 0 1563275898.6722345
# 1 1563275899.673589
# 2 1563275900.6750457
# 3 1563275901.6763387
# 4 1563275902.6777005
```

## License

**aiothrottling** is released under the BSD 2-Clause License.
