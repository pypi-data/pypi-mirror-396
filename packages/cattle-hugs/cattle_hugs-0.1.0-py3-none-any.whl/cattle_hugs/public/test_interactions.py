from cattle_hugs.testing import *  # noqa

from .objects import register_base_object
from .interactions import retrieve_interactions
from ..types import Interactions


async def test_retrieve_interactions_no_response(sql_session):
    result = await retrieve_interactions(sql_session, "http://object.test/some/id")

    assert result is None


async def test_retrieve_interactions_response(sql_session):
    object_id = "http://object.test/some/id"

    await register_base_object(sql_session, {"id": object_id})

    result = await retrieve_interactions(sql_session, object_id)

    assert isinstance(result, Interactions)
    assert result.object_id == object_id
