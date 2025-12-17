from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


class ChatUpdateMuteRequest(BaseModel):
    """Request to mute/unmute a chat. Set duration to None to unmute."""
    model_config = ConfigDict(populate_by_name=True)

    duration: Optional[Literal["8h", "1w", "always"]] = Field(default=None, alias="duration")