import pytest


from cattle_hugs.database.models import StoredActor
from cattle_hugs.database.object_models import BaseObject, Comment, CommentStatus
from cattle_hugs.processing.trees import determine_base_object
from cattle_hugs.testing import *  # noqa


@pytest.fixture
async def base_object(sql_session):
    base_id = "http://base.test/object/id"

    base = BaseObject(object_id=base_id)
    sql_session.add(base)
    await sql_session.commit()
    await sql_session.refresh(base)
    return base


@pytest.fixture
async def base_object_id(base_object):
    return base_object.object_id


@pytest.fixture
async def actor_obj(sql_session):
    actor = StoredActor(id="http://actor.test/id", data={})
    sql_session.add(actor)
    await sql_session.commit()
    await sql_session.refresh(actor)
    return actor


@pytest.fixture
async def reply_object_id(sql_session, actor_obj, base_object):
    obj_id = "http://obj.test/object/id"

    comment = Comment(
        base_object=base_object,
        actor=actor_obj,
        object_id=obj_id,
        in_reply_to=base_object.object_id,
        data={"id": obj_id},
        status=CommentStatus.reply,
    )
    sql_session.add(comment)
    await sql_session.commit()

    return obj_id


async def test_unknown_object(sql_session):
    result = await determine_base_object(sql_session, "http://unknown.test")

    assert result is None


async def test_known_base_object(sql_session, base_object_id):
    result = await determine_base_object(sql_session, base_object_id)

    assert result
    assert result.object_id == base_object_id


async def test_known_reply_object(sql_session, base_object_id, reply_object_id):
    result = await determine_base_object(sql_session, reply_object_id)

    assert result
    assert result.object_id == base_object_id
