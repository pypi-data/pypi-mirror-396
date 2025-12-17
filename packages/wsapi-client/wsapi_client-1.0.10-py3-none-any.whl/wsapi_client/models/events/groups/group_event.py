from __future__ import annotations
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from ...entities.users.sender import Sender


class GroupDescription(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    topic: Optional[str] = None


class GroupEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    sender: Optional[Sender] = None
    description: Optional[GroupDescription] = None
    timestamp: Optional[datetime] = None
    join: Optional[List[str]] = None
    leave: Optional[List[str]] = None
