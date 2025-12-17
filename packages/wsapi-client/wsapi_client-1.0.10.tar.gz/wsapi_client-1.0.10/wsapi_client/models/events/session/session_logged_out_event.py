from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict


class SessionLoggedOutEvent(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    reason: Optional[str] = None
