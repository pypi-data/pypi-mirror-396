import logging
from cattle_grid.extensions import Extension
from cattle_grid.extensions.util import lifespan_for_sql_alchemy_base_class

from cattle_hugs.database.models import Base

from .for_actor import handle_delete, handle_update
from .objects import (
    handle_create,
    handle_like_announce,
    handle_undo,
    handle_delete as handle_delete_object,
    handle_update as handle_update_object,
)

logger = logging.getLogger(__name__)
extension = Extension(
    "Cattle Hugs",
    __name__,
    lifespan=lifespan_for_sql_alchemy_base_class(Base),  # type: ignore
)


def in_and_out(activity, method):
    return [(f"incoming.{activity}", method), (f"outgoing.{activity}", method)]


for routing_key, method in sum(
    (
        in_and_out(activity, method)
        for activity, method in [
            ("Update", handle_update),
            ("Delete", handle_delete),
            ("Like", handle_like_announce),
            ("Announce", handle_like_announce),
            ("Undo", handle_undo),
            ("Create", handle_create),
            ("Delete", handle_delete_object),
            ("Update", handle_update_object),
        ]
    ),
    [],
):
    extension.subscribe(routing_key)(method)
