from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class GroupSetLockedRequest(BaseModel):
    locked: bool = Field(alias="locked")

    model_config = ConfigDict(populate_by_name=True)
