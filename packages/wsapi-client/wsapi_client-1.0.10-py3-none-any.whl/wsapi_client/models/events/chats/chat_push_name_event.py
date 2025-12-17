from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class ChatPushNameEvent(BaseModel):
    """Event for chat push name updates."""
    model_config = ConfigDict(populate_by_name=True)

    id: str
    push_name: str = Field(alias="pushName")
