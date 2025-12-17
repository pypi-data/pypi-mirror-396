from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class GroupJoined(BaseModel):
    group_id: str = Field(alias="groupId")

    model_config = ConfigDict(populate_by_name=True)
