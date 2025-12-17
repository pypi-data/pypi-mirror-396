from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class GroupSetAnnounceRequest(BaseModel):
    announce: bool = Field(alias="announce")

    model_config = ConfigDict(populate_by_name=True)
