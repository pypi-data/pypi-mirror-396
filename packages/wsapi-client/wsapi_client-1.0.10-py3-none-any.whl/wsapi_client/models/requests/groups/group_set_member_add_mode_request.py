from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict


class GroupSetMemberAddModeRequest(BaseModel):
    only_admins: bool = Field(alias="onlyAdmins")

    model_config = ConfigDict(populate_by_name=True)
