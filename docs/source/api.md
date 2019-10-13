API
===

rates
-----

Pass the rate in the format `{limit}/{base period name}` or `{limit}/{factor}{base period name}`, for example

- full period name
    + `1/second`, `2/minute`, `3/hour`, `4/day`
- short period name
    + `4/s`, `5/m`, `6/h`, `7/d`
- set custom period by using a factor
    + `1/3s`, `12/37m`, `1/5h`, `8/3d`

Throttle Class
--------------

.. currentmodule:: aiothrottling.Throttle

.. autofunction:: __init__
.. autofunction:: delay

DistributedThrottle Class
-------------------------

.. currentmodule:: aiothrottling.DistributedThrottle

.. autofunction:: __init__
.. autofunction:: pk
.. autofunction:: block
.. autofunction:: flush
.. autofunction:: acquire

Lock Class
----------

.. currentmodule:: aiothrottling.Lock

.. autofunction:: __init__
.. autofunction:: acquire
.. autofunction:: release
.. autofunction:: check_in
.. autofunction:: check
.. autofunction:: check_out
