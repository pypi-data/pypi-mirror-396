from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, Type

from pydantic import TypeAdapter

from ..models.events.base_event import BaseEvent
from ..models.events.messages.message_star_event import MessageStarEvent
from ..models.events.messages.message_read_event import MessageReadEvent
from ..models.events.messages.message_event import MessageEvent
from ..models.events.messages.message_delete_event import MessageDeleteEvent
from ..models.events.messages.message_history_sync_event import MessageHistorySyncEvent
from ..models.events.contacts.contact_event import ContactEvent
from ..models.events.users.user_presence_event import UserPresenceEvent
from ..models.events.calls.call_offer_event import CallOfferEvent
from ..models.events.calls.call_accept_event import CallAcceptEvent
from ..models.events.calls.call_terminate_event import CallTerminateEvent
from ..models.events.chats.chat_presence_event import ChatPresenceEvent
from ..models.events.chats.chat_setting_event import ChatSettingEvent
from ..models.events.chats.chat_push_name_event import ChatPushNameEvent
from ..models.events.chats.chat_status_event import ChatStatusEvent
from ..models.events.chats.chat_picture_event import ChatPictureEvent
from ..models.events.groups.group_event import GroupEvent
from ..models.events.session.session_logged_in_event import SessionLoggedInEvent
from ..models.events.session.session_logged_out_event import SessionLoggedOutEvent
from ..models.events.session.session_logged_error_event import SessionLoggedErrorEvent
from ..models.events.session.initial_sync_finished_event import InitialSyncFinishedEvent


_EVENT_TYPES: Dict[str, Type[Any]] = {
    # Session events
    "logged_in": SessionLoggedInEvent,
    "logged_out": SessionLoggedOutEvent,
    "logged_error": SessionLoggedErrorEvent,
    "initial_sync_finished": InitialSyncFinishedEvent,
    # Chat events
    "chat_presence": ChatPresenceEvent,
    "chat_setting": ChatSettingEvent,
    "chat_push_name": ChatPushNameEvent,
    "chat_status": ChatStatusEvent,
    "chat_picture": ChatPictureEvent,
    # Message events
    "message": MessageEvent,
    "message_delete": MessageDeleteEvent,
    "message_history_sync": MessageHistorySyncEvent,
    "message_read": MessageReadEvent,
    "message_star": MessageStarEvent,
    # Contact events
    "contact": ContactEvent,
    # Group events
    "group": GroupEvent,
    # User events
    "user_presence": UserPresenceEvent,
    # Call events
    "call_offer": CallOfferEvent,
    "call_accept": CallAcceptEvent,
    "call_terminate": CallTerminateEvent,
}


def parse_event(raw_json: str) -> BaseEvent:
    import json

    if not raw_json:
        raise ValueError("JSON cannot be empty")
    obj = json.loads(raw_json)

    # Validate base props
    if "receivedAt" not in obj or "instanceId" not in obj or "eventType" not in obj or "eventData" not in obj:
        raise ValueError("Missing required event fields")

    event_type = obj["eventType"]
    if event_type not in _EVENT_TYPES:
        raise ValueError(f"Unknown event type: {event_type}")

    model = _EVENT_TYPES[event_type]
    data = obj["eventData"]

    # Deserialize payload
    payload = TypeAdapter(model).validate_python(data)

    # Inject base props for convenience if payload doesn’t derive BaseEvent
    base = BaseEvent.model_validate({
        "instanceId": obj["instanceId"],
        "receivedAt": obj["receivedAt"],
        "eventType": event_type,
    })

    # Attach base info dynamically
    # For now, return the payload; callers can use base separately if needed.
    # Future: create a wrapper type with .base and .data
    payload._base = base  # type: ignore[attr-defined]
    return payload  # type: ignore[return-value]
