from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from cattle_hugs.database.object_models import BaseObject, CommentStatus

from ..types import InteractionInfo, Interactions, CommentInfo


async def retrieve_interactions(session: AsyncSession, object_id: str):
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

    return Interactions(
        object_id=object_id, comments=comments, interactions=interactions
    )
