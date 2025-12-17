from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from ...entities.users.sender import Sender


class ChatPictureEvent(BaseModel):
    """Event for chat picture updates."""
    model_config = ConfigDict(populate_by_name=True)

    id: str
    sender: Sender
    picture_id: str = Field(alias="pictureId")
