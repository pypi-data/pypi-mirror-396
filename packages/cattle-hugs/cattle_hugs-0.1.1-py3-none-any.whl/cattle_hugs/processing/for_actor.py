import logging

from cattle_grid.dependencies import SqlSession
from muck_out.cattle_grid import ParsedEmbeddedActor, ParsedActivity
from sqlalchemy import delete, select
from sqlalchemy.orm.attributes import flag_modified

from cattle_hugs.database.models import StoredActor

logger = logging.getLogger(__name__)


async def handle_update(sql_session: SqlSession, embedded_actor: ParsedEmbeddedActor):
    if not embedded_actor:
        return

    in_db = await sql_session.scalar(
        select(StoredActor).where(StoredActor.id == embedded_actor.id)
    )

    if not in_db:
        return

    in_db.data = embedded_actor.model_dump(exclude_none=True)
    flag_modified(in_db, "data")

    await sql_session.commit()


async def handle_delete(sql_session: SqlSession, activity: ParsedActivity):
    if not activity:
        return
    if activity.object != activity.actor:
        return

    logger.info("deleting actor with id %s", activity.actor)

    await sql_session.execute(
        delete(StoredActor).where(StoredActor.id == activity.actor)
    )
    await sql_session.commit()
