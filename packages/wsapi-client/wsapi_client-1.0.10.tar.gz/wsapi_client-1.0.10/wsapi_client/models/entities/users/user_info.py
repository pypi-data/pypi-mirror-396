from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserInfo(BaseModel):
    """User information returned from GET /users/{phone}."""
    model_config = ConfigDict(populate_by_name=True)

    jid: Optional[str] = None
    name: Optional[str] = None
    status: Optional[str] = None
