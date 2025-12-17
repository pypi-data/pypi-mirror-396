from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class GroupSetJoinApprovalRequest(BaseModel):
    join_approval: bool = Field(alias="joinApproval")

    model_config = ConfigDict(populate_by_name=True)
