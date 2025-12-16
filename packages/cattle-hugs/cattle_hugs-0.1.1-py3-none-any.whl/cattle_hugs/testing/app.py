from contextlib import asynccontextmanager
from fastapi import FastAPI, Request

from cattle_grid.app import app_globals
from cattle_grid.database import database_engine

from cattle_hugs.public.objects import with_collections
from cattle_hugs.public.objects_server import object_router


object_id = "http://runner/object_id"
served_object = {
    "type": "Note",
    "attributedTo": "http://remote/actor",
    "id": object_id,
    "to": ["https://www.w3.org/ns/activitystreams#Public"],
    "cc": [],
}


@asynccontextmanager
async def lifespan(*args):
    async with database_engine(db_url=app_globals.config.db_url) as engine:
        app_globals.engine = engine

        yield


async def add_activity_pub_headers(request: Request, call_next):
    request.scope["headers"].append((b"x-ap-location", str(request.url).encode()))

    response = await call_next(request)
    return response


def create_app():
    app = FastAPI(lifespan=lifespan)

    app.middleware("http")(add_activity_pub_headers)

    @app.get("/object_id")
    async def object_result():
        return with_collections(served_object)

    app.include_router(object_router)

    return app
