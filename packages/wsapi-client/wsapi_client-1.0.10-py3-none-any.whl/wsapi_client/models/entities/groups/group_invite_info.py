from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict
from .group_participant_info import GroupParticipantInfo


class GroupInviteInfo(BaseModel):
    """Group information returned from invite code lookup (GET /groups/invite/{code})."""
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="id")
    owner_id: str = Field(alias="ownerId")
    name: str = Field(alias="name")
    created: datetime = Field(alias="created")
    description: Optional[str] = Field(default=None, alias="description")
    is_announce: bool = Field(alias="isAnnounce")
    is_locked: bool = Field(alias="isLocked")
    is_ephemeral: bool = Field(alias="isEphemeral")
    ephemeral_expiration: Optional[int] = Field(default=None, alias="ephemeralExpiration")
    participants: List[GroupParticipantInfo] = Field(alias="participants")
