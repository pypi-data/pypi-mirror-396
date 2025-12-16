from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from cattle_hugs.database.object_models import BaseObject, CommentStatus
from muck_out.types import Actor
from ..types import InteractionInfo, Interactions, CommentInfo


async def retrieve_interactions(
    session: AsyncSession, object_id: str
) -> None | Interactions:
    """Returns the interactions"""
    result = await session.scalar(
        select(BaseObject)
        .where(BaseObject.object_id == object_id)
        .options(joinedload(BaseObject.comments))
        .options(joinedload(BaseObject.interactions))
    )

    if not result:
        return

    comments = [
        CommentInfo(data=x.data)
        for x in result.comments
        if x.status != CommentStatus.deleted
    ]
    interactions = [
        InteractionInfo(interaction_type=x.interaction_type, data=x.activity)
        for x in result.interactions
    ]

    actors_for_id = {}
    for x in result.comments:
        actors_for_id[x.actor.id] = Actor.model_validate(x.actor.data)
    for x in result.interactions:
        actors_for_id[x.actor.id] = Actor.model_validate(x.actor.data)

    actors = list(actors_for_id.values())

    return Interactions(
        object_id=object_id, comments=comments, interactions=interactions, actors=actors
    )
