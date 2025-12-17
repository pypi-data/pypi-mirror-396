from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class GroupParticipantInfo(BaseModel):
    """Group participant information with optional admin status fields."""
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="id")
    is_admin: Optional[bool] = Field(default=None, alias="isAdmin")
    is_super_admin: Optional[bool] = Field(default=None, alias="isSuperAdmin")
    display_name: Optional[str] = Field(default=None, alias="displayName")