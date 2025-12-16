from enum import StrEnum, auto
from sqlalchemy import JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .models import Base, StoredActor


from cattle_hugs.types import InteractionType


class BaseObject(Base):
    __tablename__ = "cattle_hugs_base_object"

    id: Mapped[int] = mapped_column(primary_key=True)
    object_id: Mapped[str] = mapped_column(unique=True)

    interactions: Mapped[list["Interaction"]] = relationship(viewonly=True)
    comments: Mapped[list["Comment"]] = relationship(viewonly=True)


class CommentStatus(StrEnum):
    reply = auto()
    quote = auto()
    deleted = auto()


class Comment(Base):
    __tablename__ = "cattle_hugs_comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    object_id: Mapped[str] = mapped_column(unique=True)

    base_object_id: Mapped[str] = mapped_column(
        ForeignKey("cattle_hugs_base_object.id")
    )
    base_object: Mapped[BaseObject] = relationship()

    in_reply_to: Mapped[str] = mapped_column()

    actor_id: Mapped[str] = mapped_column(ForeignKey("cattle_hugs_stored_actor.id"))
    actor: Mapped[StoredActor] = relationship(lazy="joined")

    status: Mapped[CommentStatus] = mapped_column()

    data: Mapped[dict] = mapped_column(JSON())


class Interaction(Base):
    __tablename__ = "cattle_hugs_interaction"

    id: Mapped[int] = mapped_column(primary_key=True)
    interaction_id: Mapped[str] = mapped_column(unique=True, nullable=True)
    interaction_type: Mapped[InteractionType] = mapped_column()

    base_object_id: Mapped[str] = mapped_column(
        ForeignKey("cattle_hugs_base_object.id")
    )
    base_object: Mapped[BaseObject] = relationship()

    actor_id: Mapped[str] = mapped_column(ForeignKey("cattle_hugs_stored_actor.id"))
    actor: Mapped[StoredActor] = relationship(lazy="joined")

    activity: Mapped[dict] = mapped_column(JSON())
