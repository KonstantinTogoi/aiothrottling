# aiothrottling
Throttles for Python coroutines.

## Example

### decorator

Use of `aiothrottling.Throttle` as decorator for coroutines:

```python
from aiothrottling import throttle  # Throttler alias
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
    await throttle
    await foo(i)

# 0 1563275898.6722345
# 1 1563275899.673589
# 2 1563275900.6750457
# 3 1563275901.6763387
# 4 1563275902.6777005
```

## License

**aiothrottling** is released under the BSD 2-Clause License.
