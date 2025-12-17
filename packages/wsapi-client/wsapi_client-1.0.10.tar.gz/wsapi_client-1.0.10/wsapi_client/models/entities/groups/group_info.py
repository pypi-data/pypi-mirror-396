from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class GroupInfo(BaseModel):
    """Group information returned from GET /groups and GET /groups/{groupId}."""
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="id")
    name: Optional[str] = Field(default=None, alias="name")
    description: Optional[str] = Field(default=None, alias="description")
    picture: Optional[str] = Field(default=None, alias="picture")
    invite_link: Optional[str] = Field(default=None, alias="inviteLink")
    participants: Optional[List[str]] = Field(default=None, alias="participants")
