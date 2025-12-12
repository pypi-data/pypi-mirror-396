import pytest

from cattle_grid.extensions.testing import with_test_broker_for_extension


from cattle_hugs.testing import *  # noqa

from . import extension


@pytest.fixture
async def test_broker():
    extension.configure({})

    async with with_test_broker_for_extension([extension]) as tbr:
        yield tbr
