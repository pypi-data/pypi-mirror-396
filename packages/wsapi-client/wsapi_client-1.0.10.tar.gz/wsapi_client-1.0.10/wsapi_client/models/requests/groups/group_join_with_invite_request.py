from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class GroupJoinWithInviteRequest(BaseModel):
    group_id: str = Field(alias="groupId")
    inviter_id: str = Field(alias="inviterId")
    code: str = Field(alias="code")
    expiration: Optional[int] = Field(default=None, alias="expiration")

    model_config = ConfigDict(populate_by_name=True)
