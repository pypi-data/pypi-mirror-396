import pytest

from cattle_hugs.testing import *  # noqa

from cattle_hugs.database.object_models import BaseObject
from .objects import InvalidObjectException, register_base_object, with_collections


async def test_register_base_object_invalid(sql_session):
    with pytest.raises(InvalidObjectException):
        await register_base_object(sql_session, {})


async def test_register_base_object(sql_session):
    object_id = "http://host.test/object/id"

    result = await register_base_object(sql_session, {"id": object_id})

    assert isinstance(result, BaseObject)
    assert result.object_id == object_id


async def test_register_base_object_twice(sql_session):
    object_id = "http://host.test/object/id"

    await register_base_object(sql_session, {"id": object_id})
    await register_base_object(sql_session, {"id": object_id})


def test_with_collections_invalid():
    with pytest.raises(InvalidObjectException):
        with_collections({})


def test_with_collections():
    object_id = "http://host.test/object/id"
    result = with_collections({"id": object_id})

    assert result["replies"] == object_id + "/replies"
