from collections import namedtuple

import pytest


Resource = namedtuple('Resource', 'name')


@pytest.fixture(params=['3/s', '6/s', '8/2s', '9/3s'])
def rate(request):
    return request.param


@pytest.fixture
def resources():
    """Test resources - named tuples with 'name' attribute."""
    return [Resource('abc'), Resource('def'), Resource('ghi')]
