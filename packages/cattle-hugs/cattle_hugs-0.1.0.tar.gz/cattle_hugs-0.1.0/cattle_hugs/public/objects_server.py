import logging
from fastapi import APIRouter

from fastapi import HTTPException

from cattle_grid.activity_pub.server.types import OrderedCollection
from cattle_grid.tools.fastapi import (
    ActivityPubHeaders,
    ActivityResponse,
)
from cattle_grid.dependencies.fastapi import SqlSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from cattle_hugs.database.object_models import (
    BaseObject,
    CommentStatus,
    InteractionType,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

object_router = APIRouter()


@object_router.get(
    "/{path}/likes",
    response_class=ActivityResponse,
    name="likes collection",
    response_model_exclude_none=True,
)
async def serve_likes(
    headers: ActivityPubHeaders,
    session: SqlSession,
) -> OrderedCollection:
    """Returns the likes"""

    in_db = await session.scalar(
        select(BaseObject)
        .where(BaseObject.object_id == headers.x_ap_location.removesuffix("/likes"))
        .options(joinedload(BaseObject.interactions))
    )
    if not in_db:
        raise HTTPException(404)

    items = [
        x.interaction_id
        for x in in_db.interactions
        if x.interaction_type in [InteractionType.like, InteractionType.emoji_reaction]
    ]

    return OrderedCollection(id=headers.x_ap_location, items=items)


@object_router.get(
    "/{path}/shares",
    response_class=ActivityResponse,
    name="shares collection",
    response_model_exclude_none=True,
)
async def serve_shares(
    headers: ActivityPubHeaders,
    session: SqlSession,
) -> OrderedCollection:
    """Returns the shares"""

    in_db = await session.scalar(
        select(BaseObject)
        .where(BaseObject.object_id == headers.x_ap_location.removesuffix("/shares"))
        .options(joinedload(BaseObject.interactions))
    )
    if not in_db:
        raise HTTPException(404)

    items = [
        x.interaction_id
        for x in in_db.interactions
        if x.interaction_type == InteractionType.share
    ]

    return OrderedCollection(id=headers.x_ap_location, items=items)


@object_router.get(
    "/{path}/replies",
    response_class=ActivityResponse,
    name="replies collection",
    response_model_exclude_none=True,
)
async def serve_replies(
    headers: ActivityPubHeaders,
    session: SqlSession,
) -> OrderedCollection:
    """Returns the replies"""

    base_object_id = headers.x_ap_location.removesuffix("/replies")

    in_db = await session.scalar(
        select(BaseObject)
        .where(BaseObject.object_id == base_object_id)
        .options(joinedload(BaseObject.comments))
    )
    if not in_db:
        raise HTTPException(404)

    items = [
        x.object_id
        for x in in_db.comments
        if x.in_reply_to == base_object_id and x.status == CommentStatus.reply
    ]

    return OrderedCollection(id=headers.x_ap_location, items=items)
