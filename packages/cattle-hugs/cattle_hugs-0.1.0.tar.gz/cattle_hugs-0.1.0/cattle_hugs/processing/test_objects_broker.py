import pytest

from sqlalchemy import select
from cattle_grid.app import app_globals
from muck_out.transform import default_public

from cattle_hugs.database.models import StoredActor
from cattle_hugs.database.object_models import Comment
from cattle_hugs import register_base_object
from .testing import *  # noqa


@pytest.fixture
async def remote_actor_id(sql_session):
    actor_id = "http://host.test/actor/123"

    sql_session.add(StoredActor(id=actor_id, data={}))
    await sql_session.commit()

    return actor_id


@pytest.fixture
def message(actor_for_test, remote_actor_id):
    return {
        "actor": actor_for_test.actor_id,
        "data": {
            "parsed": {
                "embedded_object": {
                    "id": "http://remote.test/note",
                    "type": "Note",
                    "attributed_to": remote_actor_id,
                    "to": [actor_for_test.actor_id, default_public],
                    "in_reply_to": "http://local.test/object/id",
                    "content": "one",
                }
            }
        },
    }


async def test_create_no_result_if_not_registred(test_broker, message, sql_session):
    await test_broker.publish(
        message,
        routing_key="incoming.Create",
        exchange=app_globals.activity_exchange,
    )

    result = await sql_session.scalar(select(Comment))

    assert not result


async def test_create(test_broker, message, sql_session):
    base_object = {"id": "http://local.test/object/id"}
    await register_base_object(sql_session, base_object)
    await sql_session.commit()

    await test_broker.publish(
        message,
        routing_key="incoming.Create",
        exchange=app_globals.activity_exchange,
    )

    result = await sql_session.scalar(select(Comment))

    assert result


async def test_create_then_update(test_broker, message, sql_session):
    base_object = {"id": "http://local.test/object/id"}
    await register_base_object(sql_session, base_object)
    await sql_session.commit()

    await test_broker.publish(
        message,
        routing_key="incoming.Create",
        exchange=app_globals.activity_exchange,
    )

    result = await sql_session.scalar(select(Comment))

    assert result.data.get("content") == "one"

    message["data"]["parsed"]["embedded_object"]["content"] = "two"
    await test_broker.publish(
        message,
        routing_key="incoming.Update",
        exchange=app_globals.activity_exchange,
    )

    await sql_session.refresh(result)

    assert result.data.get("content") == "two"
