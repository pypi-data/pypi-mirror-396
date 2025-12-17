from __future__ import annotations
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class AccountUpdatePresenceRequest(BaseModel):
    """Request to update account presence status."""
    model_config = ConfigDict(populate_by_name=True)

    status: Literal["available", "unavailable"] = Field(alias="status")