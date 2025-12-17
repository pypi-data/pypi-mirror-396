from __future__ import annotations
from typing import Optional, Literal
from pydantic import BaseModel, Field, ConfigDict


class MessageSendLocationRequest(BaseModel):
    to: str = Field(alias="to")
    latitude: float = Field(alias="latitude")
    longitude: float = Field(alias="longitude")
    name: Optional[str] = Field(default=None, alias="name")
    address: Optional[str] = Field(default=None, alias="address")
    url: Optional[str] = Field(default=None, alias="url")
    ephemeral_expiration: Optional[Literal["24h", "7d", "90d"]] = Field(default=None, alias="ephemeralExpiration")

    model_config = ConfigDict(populate_by_name=True)
