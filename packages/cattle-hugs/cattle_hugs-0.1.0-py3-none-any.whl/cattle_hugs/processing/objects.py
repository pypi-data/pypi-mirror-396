from collections.abc import Awaitable
from dataclasses import dataclass
import logging
from typing import Annotated
from collections.abc import Callable
from fast_depends import Depends
from muck_out.cattle_grid import ParsedActivity, FetchActor, ParsedEmbeddedObject
from cattle_grid.dependencies import SqlSession
from cattle_grid.model.common import WithActor
from muck_out.types.validated.actor import Actor
from sqlalchemy import select

from muck_out.types import Activity
from muck_out.transform import default_public

from cattle_hugs.database.models import StoredActor
from cattle_hugs.database.object_models import (
    BaseObject,
    Comment,
    CommentStatus,
    Interaction,
    InteractionType,
)
from cattle_hugs.processing.trees import determine_base_object
from cattle_hugs.public import db_actor_for_id

logger = logging.getLogger(__name__)


def determine_interaction_type(activity: Activity):
    if activity.type == "Announce":
        return InteractionType.share
    if activity.type != "Like":
        raise Exception("Found unexpected activity type")
    if activity.content:
        return InteractionType.emoji_reaction
    return InteractionType.like


@dataclass
class ActorResolverClass:
    session: SqlSession
    message: WithActor
    fetch_actor: FetchActor

    async def _fetch(self, actor_id: str) -> Actor | None:
        return await self.fetch_actor(self.message.actor, actor_id)

    async def __call__(self, actor_id) -> StoredActor:
        return await db_actor_for_id(self.session, self._fetch, actor_id)


ActorResolver = Annotated[
    Callable[[str], Awaitable[StoredActor]], Depends(ActorResolverClass)
]


async def handle_like_announce(
    session: SqlSession, actor_resolver: ActorResolver, activity: ParsedActivity
):
    if not activity:
        return

    base_object = await session.scalar(
        select(BaseObject).where(BaseObject.object_id == activity.object)
    )

    if not base_object:
        return

    actor = await actor_resolver(activity.actor)

    interaction = Interaction(
        interaction_id=activity.id,
        base_object=base_object,
        interaction_type=determine_interaction_type(activity),
        activity=activity.model_dump(mode="json", exclude_none=True),
        actor=actor,
    )

    session.add(interaction)

    await session.commit()


async def handle_undo(
    activity: ParsedActivity,
    session: SqlSession,
):
    if activity is None:
        return
    in_db = await session.scalar(
        select(Interaction).where(Interaction.interaction_id == activity.object)
    )
    if not in_db:
        return
    if in_db.actor.id != activity.actor:
        return

    await session.delete(in_db)
    await session.commit()


async def handle_create(
    obj: ParsedEmbeddedObject,
    session: SqlSession,
    actor_resolver: ActorResolver,
):
    if obj is None or obj.in_reply_to is None:
        logger.debug("Not a reply")
        return

    if obj.sensitive:
        return

    if default_public not in (obj.to + obj.cc):
        logger.debug("Not public")
        return

    base_page = await determine_base_object(session, obj.in_reply_to)
    if not base_page:
        logger.debug("No base object")
        return

    actor = await actor_resolver(obj.attributed_to)

    comment = Comment(
        base_object=base_page,
        actor=actor,
        object_id=obj.id,
        in_reply_to=obj.in_reply_to,
        data=obj.model_dump(mode="json"),
        status=CommentStatus.reply,
    )

    session.add(comment)
    await session.commit()


async def handle_delete(
    session: SqlSession,
    activity: ParsedActivity,
):
    if not activity:
        return
    if not activity.object:
        return

    comment = await session.scalar(
        select(Comment).where(Comment.object_id == activity.object)
    )

    if comment:
        comment.status = CommentStatus.deleted
        await session.commit()


async def handle_update(
    obj: ParsedEmbeddedObject,
    session: SqlSession,
    actor_resolver: ActorResolver,
):
    if obj is None:
        logger.debug("No object")
        return

    comment = await session.scalar(select(Comment).where(Comment.object_id == obj.id))
    if not comment:
        logger.debug("No comment found")
        return

    if obj.attributed_to != comment.actor_id:
        logger.warning("Mismatch between actors for update")
        return

    logger.info("Updating comment")

    comment.data = obj.model_dump(mode="json")
    await session.commit()
