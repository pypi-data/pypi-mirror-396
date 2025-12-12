from unittest.mock import AsyncMock
import pytest

from cattle_grid.testing.fixtures import *  # type: ignore  # noqa: F403
from cattle_grid.extensions.util import lifespan_for_sql_alchemy_base_class

from muck_out.types import Actor

from ..database.models import Base


@pytest.fixture(autouse=True)
async def create_tables(sql_engine_for_tests):
    lifespan = lifespan_for_sql_alchemy_base_class(Base)
    async with lifespan(sql_engine_for_tests):
        yield


@pytest.fixture
def actor_id():
    return "http://host.test/actor/id"


@pytest.fixture
def mock_actor(actor_id):
    return Actor(
        type="Person",
        id=actor_id,
        inbox=f"{actor_id}/inbox",
        outbox=f"{actor_id}/outbox",
        identifiers=["acct:test@host.test"],
    )  # type: ignore


@pytest.fixture
def mock_fetcher(mock_actor):
    return AsyncMock(return_value=mock_actor)
