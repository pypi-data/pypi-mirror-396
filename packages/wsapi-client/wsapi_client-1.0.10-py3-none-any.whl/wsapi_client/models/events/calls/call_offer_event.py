from __future__ import annotations
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class CallOfferEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    caller: str
    chat_id: str = Field(alias="chatId")
    time: datetime
    is_group: Optional[bool] = Field(default=None, alias="isGroup")
    is_video: Optional[bool] = Field(default=None, alias="isVideo")
