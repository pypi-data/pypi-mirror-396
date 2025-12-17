from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class ChatUpdatePresenceRequest(BaseModel):
    """Request to update chat presence state."""
    model_config = ConfigDict(populate_by_name=True)

    state: Literal["typing", "recording", "paused"] = Field(alias="state")