from collections.abc import Awaitable, Callable
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from muck_out.types import Actor

from cattle_hugs.database.models import StoredActor


class ActorNotFoundError(Exception): ...


async def db_actor_for_id(
    session: AsyncSession,
    fetcher: Callable[[str], Awaitable[Actor | None]],
    actor_id: str,
) -> StoredActor:
    in_db = await session.scalar(select(StoredActor).where(StoredActor.id == actor_id))

    if in_db:
        return in_db

    result = await fetcher(actor_id)

    if result is None:
        raise ActorNotFoundError(f"Actor not found: {actor_id}")

    actor_to_store = StoredActor(
        id=result.id, data=result.model_dump(exclude_none=True)
    )
    session.add(actor_to_store)
    await session.commit()
    await session.refresh(actor_to_store)

    return actor_to_store


async def actor_for_id(
    session: AsyncSession,
    fetcher: Callable[[str], Awaitable[Actor | None]],
    actor_id: str,
) -> Actor:
    in_db = await db_actor_for_id(session, fetcher, actor_id)

    return Actor.model_validate(in_db.data)
