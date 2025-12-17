from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class MessageSendReactionRequest(BaseModel):
    to: str = Field(alias="to")
    sender_id: str = Field(alias="senderId")
    reaction: str = Field(alias="reaction")

    model_config = ConfigDict(populate_by_name=True)
