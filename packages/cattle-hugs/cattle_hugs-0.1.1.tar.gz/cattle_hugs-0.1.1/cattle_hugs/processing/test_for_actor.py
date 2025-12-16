import pytest

from cattle_grid.app import app_globals
from sqlalchemy import select

from cattle_hugs.database.models import StoredActor
from cattle_hugs.public import ActorNotFoundError, actor_for_id

from .testing import *  # noqa


async def test_handle_update(test_broker, actor_for_test):
    await test_broker.publish(
        {"actor": actor_for_test.actor_id, "data": {}},
        routing_key="incoming.Update",
        exchange=app_globals.activity_exchange,
    )


async def test_handle_update_parsed_actor_ignores_if_not_in_db(
    test_broker, sql_session, actor_id, mock_fetcher, actor_for_test
):
    await test_broker.publish(
        {
            "actor": actor_for_test.actor_id,
            "data": {
                "parsed": {
                    "embedded_actor": {
                        "id": actor_id,
                        "type": "Person",
                        "inbox": f"{actor_id}/inbox",
                        "outbox": f"{actor_id}/outbox",
                        "identifiers": ["acct:other@host.test"],
                        "name": "I now have a name",
                    }
                }
            },
        },
        routing_key="incoming.Update",
        exchange=app_globals.activity_exchange,
    )

    result = await sql_session.scalars(select(StoredActor))

    assert result.all() == []


async def test_handle_update_parsed_actor(
    test_broker, sql_session, actor_id, mock_fetcher, actor_for_test
):
    result = await actor_for_id(sql_session, mock_fetcher, actor_id)
    assert result.name is None

    await test_broker.publish(
        {
            "actor": actor_for_test.actor_id,
            "data": {
                "parsed": {
                    "embedded_actor": {
                        "id": actor_id,
                        "type": "Person",
                        "inbox": f"{actor_id}/inbox",
                        "outbox": f"{actor_id}/outbox",
                        "identifiers": ["acct:other@host.test"],
                        "name": "I now have a name",
                    }
                }
            },
        },
        routing_key="incoming.Update",
        exchange=app_globals.activity_exchange,
    )

    result = await actor_for_id(sql_session, mock_fetcher, actor_id)
    assert result.name == "I now have a name"


async def test_delete_actor(
    test_broker, sql_session, actor_for_test, actor_id, mock_fetcher
):
    await actor_for_id(sql_session, mock_fetcher, actor_id)

    await test_broker.publish(
        {
            "actor": actor_for_test.actor_id,
            "data": {
                "parsed": {
                    "activity": {
                        "type": "Delete",
                        "id": actor_id + "/delete",
                        "actor": actor_id,
                        "object": actor_id,
                        "to": ["https://www.w3.org/ns/activitystreams#Public"],
                        "cc": [],
                    }
                }
            },
        },
        routing_key="incoming.Delete",
        exchange=app_globals.activity_exchange,
    )
    mock_fetcher.return_value = None

    with pytest.raises(ActorNotFoundError):
        await actor_for_id(sql_session, mock_fetcher, actor_id)
