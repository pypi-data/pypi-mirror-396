from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cattle_hugs.database.object_models import BaseObject, Comment


async def determine_base_object(
    session: AsyncSession, object_id: str
) -> BaseObject | None:
    base_obj = await session.scalar(
        select(BaseObject).where(BaseObject.object_id == object_id)
    )

    if base_obj:
        return base_obj

    reply = await session.scalar(select(Comment).where(Comment.object_id == object_id))

    if reply:
        return reply.base_object

    return None
