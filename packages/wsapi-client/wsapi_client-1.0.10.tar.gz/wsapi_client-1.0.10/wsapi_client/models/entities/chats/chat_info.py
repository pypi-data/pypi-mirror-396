from __future__ import annotations
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class ChatInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # Required fields per OpenAPI spec
    id: str = Field(alias="id")
    is_read_only: bool = Field(alias="isReadOnly")
    is_group: bool = Field(alias="isGroup")
    is_archived: bool = Field(alias="isArchived")
    is_pinned: bool = Field(alias="isPinned")
    is_ephemeral: bool = Field(alias="isEphemeral")
    is_muted: bool = Field(alias="isMuted")
    is_spam: bool = Field(alias="isSpam")

    # Optional fields per OpenAPI spec
    lid: Optional[str] = Field(default=None, alias="lid")
    ephemeral_expiration: Optional[Literal["off", "24h", "7d", "90d"]] = Field(default=None, alias="ephemeralExpiration")
    mute_end_time: Optional[datetime] = Field(default=None, alias="muteEndTime")
    business_name: Optional[str] = Field(default=None, alias="businessName")
    push_name: Optional[str] = Field(default=None, alias="pushName")
    status: Optional[str] = Field(default=None, alias="status")
