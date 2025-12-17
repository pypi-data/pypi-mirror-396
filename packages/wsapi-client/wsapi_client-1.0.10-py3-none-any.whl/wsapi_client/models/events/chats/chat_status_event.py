from __future__ import annotations
from pydantic import BaseModel, ConfigDict


class ChatStatusEvent(BaseModel):
    """Event for chat status updates."""
    model_config = ConfigDict(populate_by_name=True)

    id: str
    status: str
