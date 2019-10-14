# aiothrottling

[![PyPI](https://img.shields.io/pypi/v/aiothrottling.svg)](https://pypi.python.org/pypi/aiothrottling)
[![PyPI version](https://img.shields.io/pypi/pyversions/aiothrottling.svg)](https://pypi.python.org/pypi/aiothrottling)

Throttles for Python coroutines.

## Getting started

aiothrottling requires python 3.5+. Install package using pip

```python
pip install aiothrottling
```

## Examples

### rates

Pass the rate in the format `{limit}/{base period name}` or `{limit}/{factor}{base period name}`, for example

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
