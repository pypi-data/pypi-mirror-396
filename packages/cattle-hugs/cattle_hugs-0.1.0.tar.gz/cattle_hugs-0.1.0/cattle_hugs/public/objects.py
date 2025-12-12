from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cattle_hugs.database.object_models import BaseObject


class InvalidObjectException(Exception): ...


def get_object_id(obj: dict) -> str:
    object_id = obj.get("id")

    if not isinstance(object_id, str):
        raise InvalidObjectException("object does not have a proper id")

    return object_id


async def register_base_object(session: AsyncSession, obj: dict):
    object_id = get_object_id(obj)

    in_db = await session.scalar(
        select(BaseObject).where(BaseObject.object_id == object_id)
    )
    if in_db:
        return in_db

    base_object = BaseObject(object_id=object_id)
    session.add(base_object)
    await session.commit()

    return base_object


def with_collections(
    obj: dict, collections: list[str] = ["replies", "shares", "likes"]
):
    object_id = get_object_id(obj)

    result = {**obj}
    for collection in collections:
        result[collection] = f"{object_id}/{collection}"

    return result
