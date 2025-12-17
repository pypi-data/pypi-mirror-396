from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ContactInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    # Required fields per OpenAPI spec
    id: str = Field(alias="id")
    full_name: str = Field(alias="fullName")
    in_phone_address_book: bool = Field(alias="inPhoneAddressBook")

    # Optional fields per OpenAPI spec
    lid: Optional[str] = Field(default=None, alias="lid")
