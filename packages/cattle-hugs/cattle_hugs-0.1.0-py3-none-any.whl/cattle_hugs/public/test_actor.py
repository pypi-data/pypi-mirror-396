from unittest.mock import AsyncMock
import pytest

from . import actor_for_id, ActorNotFoundError
from cattle_hugs.testing import *  # noqa


async def test_actor_for_id(sql_session, mock_fetcher, mock_actor):
    actor_id = "http://host.test/actor/id"
    result = await actor_for_id(sql_session, mock_fetcher, "http://host.test/actor/id")

    assert result == mock_actor

    mock_fetcher.assert_awaited_once_with(actor_id)


async def test_actor_for_id_not_found(sql_session):
    fetcher = AsyncMock(return_value=None)

    with pytest.raises(ActorNotFoundError):
        await actor_for_id(sql_session, fetcher, "http://host.test/actor/id")


async def test_actor_for_id_not_fetched_twice(sql_session, mock_fetcher):
    actor_id = "http://host.test/actor/id"

    await actor_for_id(sql_session, mock_fetcher, "http://host.test/actor/id")
    await actor_for_id(sql_session, mock_fetcher, "http://host.test/actor/id")

    mock_fetcher.assert_awaited_once_with(actor_id)
