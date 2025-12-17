from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class MessageLocation(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    latitude: float = Field(alias="latitude")
    longitude: float = Field(alias="longitude")
    name: Optional[str] = Field(default=None, alias="name")
    address: Optional[str] = Field(default=None, alias="address")
    url: Optional[str] = Field(default=None, alias="url")
