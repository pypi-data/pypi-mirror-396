from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from ...entities.users.sender import Sender
from ...entities.messages.message_reply_to import MessageReplyTo
from ...entities.messages.message_extended_text import MessageExtendedText
from ...entities.messages.message_edit import MessageEdit
from ...entities.messages.message_media import MessageMedia
from ...entities.messages.message_reaction import MessageReaction
from ...entities.messages.message_contact import MessageContact
from ...entities.messages.message_pin import MessagePin
from ...entities.messages.message_location import MessageLocation


class MessageEvent(BaseModel):
    """Message event data as defined in the OpenAPI spec."""
    model_config = ConfigDict(populate_by_name=True)

    # Required fields per spec
    id: str
    chat_id: str = Field(alias="chatId")
    sender: Sender
    time: datetime
    type: str

    # Optional fields per spec
    is_group: Optional[bool] = Field(default=None, alias="isGroup")
    is_status: Optional[bool] = Field(default=None, alias="isStatus")
    mentions: Optional[list[str]] = Field(default=None, alias="mentions")
    ephemeral_expiration: Optional[str] = Field(default=None, alias="ephemeralExpiration")
    is_edit: Optional[bool] = Field(default=None, alias="isEdit")

    # Message content fields (mutually exclusive based on type)
    text: Optional[str] = Field(default=None, alias="text")
    reply_to: Optional[MessageReplyTo] = Field(default=None, alias="replyTo")
    extended_text: Optional[MessageExtendedText] = Field(default=None, alias="extendedText")
    edit: Optional[MessageEdit] = Field(default=None, alias="edit")
    media: Optional[MessageMedia] = Field(default=None, alias="media")
    reaction: Optional[MessageReaction] = Field(default=None, alias="reaction")
    contact: Optional[str] = Field(default=None, alias="contact")
    contacts: Optional[list[str]] = Field(default=None, alias="contactArray")
    pin: Optional[MessagePin] = Field(default=None, alias="pin")
    location: Optional[MessageLocation] = Field(default=None, alias="location")
