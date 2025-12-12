from pydantic import BaseModel, Field

from enum import StrEnum, auto


class InteractionType(StrEnum):
    share = auto()
    like = auto()
    emoji_reaction = auto()


class CommentInfo(BaseModel):
    data: dict


class InteractionInfo(BaseModel):
    interaction_type: InteractionType
    data: dict


class Interactions(BaseModel):
    object_id: str = Field(description="The object that was interacted with")
    comments: list[CommentInfo] = Field(
        description="All comments made to the base object"
    )
    interactions: list[InteractionInfo] = Field(
        description="Interactions, e.g likes, of the base object"
    )
