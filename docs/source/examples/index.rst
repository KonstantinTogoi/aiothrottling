Examples
========

Examples use *coroutines* exclusively.

Setting the throttling rate
---------------------------

The allowed coroutine call rate is determined by the ``rate`` argument.
Pass the rate in the format ``{limit}/{base period name}`` or ``{limit}/{factor}{base period name}``, for example

- full period name
    + `1/second`, `2/minute`, `3/hour`, `4/day`
- short period name
    + `4/s`, `5/m`, `6/h`, `7/d`
- set custom period by using a factor
    + `1/3s`, `12/37m`, `1/5h`, `8/3d`

.. toctree::
    :maxdepth: 2

    simple
    distributed
