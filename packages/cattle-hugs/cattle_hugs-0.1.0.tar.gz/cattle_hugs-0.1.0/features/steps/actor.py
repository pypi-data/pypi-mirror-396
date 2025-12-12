from behave_auto_docstring import when, then, given
from cattle_grid.testing.features import fetch_request, publish_as
from cattle_grid.model.exchange import UpdateActorMessage

from cattle_grid.app import app_globals
from cattle_grid.database import database_engine

from muck_out.process import normalize_actor
from sqlalchemy.ext.asyncio import async_sessionmaker

from cattle_hugs import actor_for_id
from cattle_hugs.public import ActorNotFoundError


@given('The actor information of "{alice}" was retrieved')
@when('The actor information of "{alice}" is retrieved')
async def retrieve_alice_information(context, alice):
    async def fetcher(actor_id: str):
        result = await fetch_request(context, alice, actor_id)
        if not result:
            return
        return normalize_actor(result)

    async with database_engine(db_url=app_globals.config.db_url) as engine:
        session_maker = async_sessionmaker(engine, expire_on_commit=False)
        async with session_maker() as sql_session:
            try:
                context.retrieved_actor = await actor_for_id(
                    sql_session, fetcher, context.actors[alice].get("id")
                )
            except ActorNotFoundError:
                context.retrieved_actor = None


@then('The result has the name "{alice}"')
def result_has_name(context, alice):
    assert context.retrieved_actor.name == alice, (
        f"Got name {context.retrieved_actor.name}"
    )


@given('"{alice}" renames herself "{new_alice}"')
async def update_name(context, alice, new_alice):
    for connection in context.connections.values():
        await connection.clear_incoming()

    alice_id = context.actors[alice].get("id")

    msg = UpdateActorMessage(actor=alice_id, profile={"name": new_alice}).model_dump()

    await publish_as(context, alice, "update_actor", msg)


@then("No result is returned")
def no_result(context):
    assert context.retrieved_actor is None, (
        f"got {context.retrieved_actor.model_dump()}"
    )
