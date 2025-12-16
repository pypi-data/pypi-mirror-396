import asyncio
from behave_auto_docstring import given

from hypercorn.config import Config
from hypercorn.asyncio import serve

from cattle_grid.app import app_globals
from cattle_grid.database import database_session
from cattle_hugs.public.objects import register_base_object


from cattle_hugs.testing.app import create_app, served_object


async def run_app():
    app = create_app()

    config = Config()
    config.bind = ["0.0.0.0:80"]

    async with database_session(db_url=app_globals.config.db_url) as session:
        await register_base_object(session, served_object)

    await serve(app, config)  # type: ignore


@given("An ActivityPub object")
async def step_impl(context):
    context.run_app_task = asyncio.create_task(run_app())
    context.activity_pub_uri = "http://runner/object_id"
