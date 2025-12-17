from __future__ import annotations
from typing import List, Literal
from pydantic import BaseModel, Field, ConfigDict


class GroupUpdateRequestsRequest(BaseModel):
    participants: List[str] = Field(alias="participants")
    action: Literal["approve", "reject"] = Field(alias="action")

    model_config = ConfigDict(populate_by_name=True)
