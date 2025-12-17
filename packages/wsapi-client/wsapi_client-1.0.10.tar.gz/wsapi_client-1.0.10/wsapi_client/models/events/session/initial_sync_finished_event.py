from __future__ import annotations
from pydantic import BaseModel, ConfigDict


class InitialSyncFinishedEvent(BaseModel):
    """Event emitted when the initial sync is finished. Event data is empty."""
    model_config = ConfigDict(populate_by_name=True)
