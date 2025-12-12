import asyncio
from cattle_grid.testing.features.environment import (
    before_all,  # noqa: F401
    before_scenario as cg_before_scenario,
    after_scenario as cg_after_scenario,
)

from cattle_grid.app import app_globals
from cattle_grid.database import database_session
from sqlalchemy import delete
from cattle_hugs.database.models import StoredActor
from cattle_hugs.database.object_models import Comment, Interaction


async def delete_objects(context):
    async with database_session(db_url=app_globals.config.db_url) as session:
        await session.execute(delete(Interaction))
        await session.execute(delete(Comment))
        await session.execute(delete(StoredActor))
        await session.commit()

    if context.run_app_task:
        context.run_app_task.cancel()
        try:
            await context.run_app_task
        except asyncio.CancelledError:
            ...


def before_scenario(context, scenario):
    context.run_app_task = None

    cg_before_scenario(context, scenario)


def after_scenario(context, scenario):
    asyncio.get_event_loop().run_until_complete(delete_objects(context))

    cg_after_scenario(context, scenario)
