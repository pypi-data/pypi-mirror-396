import json
from behave_auto_docstring import then

from cattle_grid.app import app_globals
from cattle_grid.database import database_engine

from sqlalchemy.ext.asyncio import async_sessionmaker

from cattle_hugs import retrieve_interactions
from cattle_hugs.types import InteractionType


@then("one get the interactions for the ActivityPub object")
async def get_interactions(context):
    async with database_engine(db_url=app_globals.config.db_url) as engine:
        session_maker = async_sessionmaker(engine, expire_on_commit=False)
        async with session_maker() as sql_session:
            context.interactions = await retrieve_interactions(
                sql_session, context.activity_pub_uri
            )


@then('the interactions contains "{text}"')
def check_interaction_content(context, text):
    replies = context.interactions.comments

    for reply in replies:
        if text in reply.data.get("content"):
            return

    assert False, f"Did not find {text}"


@then('the interactions does not contain "{text}"')
def check_interaction_content_not_contain(context, text):
    replies = context.interactions.comments

    for reply in replies:
        assert text not in reply.data.get("content"), (
            f"Found in {json.dumps(reply.data)}"
        )


@then('the number of "{interaction_type}" in the interactions is "{number}"')
def count_interactions(context, interaction_type, number):
    cast_type = InteractionType(interaction_type.removesuffix("s"))

    interactions = context.interactions.interactions
    filtered = [x for x in interactions if x.interaction_type == cast_type]

    assert len(filtered) == int(number)
