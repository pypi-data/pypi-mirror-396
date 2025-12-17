from __future__ import annotations
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


EventFilterType = Literal[
    "message",
    "message_read",
    "message_delete",
    "message_star",
    "message_history_sync",
    "chat_setting",
    "chat_presence",
    "chat_push_name",
    "chat_status",
    "chat_picture",
    "contact",
    "group",
    "user_presence",
    "call_offer",
    "call_terminate",
    "call_accept",
    "logged_error",
    "logged_out",
    "logged_in",
    "initial_sync_finished",
]


class InstanceSettings(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: Optional[str] = Field(default=None, alias="name")
    description: Optional[str] = Field(default=None, alias="description")
    webhook_url: Optional[str] = Field(default=None, alias="webhookUrl")
    webhook_auth_header: Optional[str] = Field(default=None, alias="webhookAuthHeader")
    webhook_auth_value: Optional[str] = Field(default=None, alias="webhookAuthValue")
    pull_mode: Optional[bool] = Field(default=None, alias="pullMode")
    event_filters: Optional[List[EventFilterType]] = Field(default=None, alias="eventFilters")
