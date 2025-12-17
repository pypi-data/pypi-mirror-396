from __future__ import annotations
from typing import List, Literal
from pydantic import BaseModel, Field, ConfigDict


class GroupUpdateParticipantsRequest(BaseModel):
    participants: List[str] = Field(alias="participants")
    action: Literal["add", "remove", "promote", "demote"] = Field(alias="action")

    model_config = ConfigDict(populate_by_name=True)
