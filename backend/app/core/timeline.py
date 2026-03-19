from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app import schemas


class TimelineBuilder:
    """
    Collects agent steps; optionally persists them.
    """

    def __init__(self, db: Optional[Session] = None):
        self._events: List[schemas.TimelineEvent] = []
        self._db = db

    def add_step(self, step: str, description: str) -> None:
        event = schemas.TimelineEvent(
            step=step,
            description=description,
            created_at=datetime.utcnow(),
        )
        self._events.append(event)

    def flush(self) -> List[schemas.TimelineEvent]:
        return list(self._events)
