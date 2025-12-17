from __future__ import annotations
from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel, Field, ConfigDict
from ...entities.users.sender import Sender


ReceiptType = Literal[
    "delivered",
    "read",
    "played",
    "readSelf",
    "sender",
    "retry",
    "serverError",
    "inactive",
    "peerMsg",
    "historySync",
]


class MessageReadEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    chat_id: str = Field(alias="chatId")
    sender: Sender
    time: datetime
    is_group: Optional[bool] = Field(default=None, alias="isGroup")
    message_sender: Optional[Sender] = Field(default=None, alias="messageSender")
    receipt_type: ReceiptType = Field(alias="receiptType")
    message_ids: Optional[list[str]] = Field(default=None, alias="messageIds")
