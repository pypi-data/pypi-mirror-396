from __future__ import annotations
from typing import Literal, Optional, List
from pydantic import BaseModel, Field, ConfigDict


class MessageSendContactRequest(BaseModel):
    """Request to send a contact message."""
    model_config = ConfigDict(populate_by_name=True)

    # Required fields
    to: str = Field(alias="to")
    v_card: str = Field(alias="vCard")

    # Optional fields
    display_name: Optional[str] = Field(default=None, alias="displayName")
    mentions: Optional[List[str]] = Field(default=None, alias="mentions")
    reply_to: Optional[str] = Field(default=None, alias="replyTo")
    is_forwarded: Optional[bool] = Field(default=None, alias="isForwarded")
    reply_to_sender_id: Optional[str] = Field(default=None, alias="replyToSenderId")
    ephemeral_expiration: Optional[Literal["24h", "7d", "90d"]] = Field(default=None, alias="ephemeralExpiration")
