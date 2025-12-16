from pydantic import BaseModel, Field

from enum import StrEnum, auto

from muck_out.types import Actor


class InteractionType(StrEnum):
    """The possible types of an interaction"""

    share = auto()
    like = auto()
    emoji_reaction = auto()


class CommentInfo(BaseModel):
    """Information about the comment"""

    data: dict


class InteractionInfo(BaseModel):
    """Information about the interaction"""

    interaction_type: InteractionType
    data: dict


class Interactions(BaseModel):
    """The Interactions"""

    object_id: str = Field(description="The object that was interacted with")
    actors: list[Actor] = Field(
        description="Information about actors participating in the interactions"
    )
    comments: list[CommentInfo] = Field(
        description="All comments made to the base object"
    )
    interactions: list[InteractionInfo] = Field(
        description="Interactions, e.g likes, of the base object"
    )
