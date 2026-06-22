from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Callable, DefaultDict, Dict, List, Optional
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class DomainEvent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    event_id: str = Field(default_factory=lambda: "event_" + uuid4().hex)
    event_type: str
    timestamp: datetime = Field(default_factory=utc_now)
    source_module: str
    aggregate_id: str
    payload: Dict[str, Any]
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


EventHandler = Callable[[DomainEvent], None]


class SharedDomainEventBus:
    """Synchronous in-process event bus for biological domain events."""

    def __init__(self) -> None:
        self._subscribers: DefaultDict[str, List[EventHandler]] = defaultdict(list)
        self._history: List[DomainEvent] = []

    @property
    def history(self) -> List[DomainEvent]:
        return list(self._history)

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        if handler not in self._subscribers[event_type]:
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: str, handler: EventHandler) -> None:
        if handler in self._subscribers[event_type]:
            self._subscribers[event_type].remove(handler)

    def publish(self, event: DomainEvent) -> None:
        self.log(event)
        for handler in list(self._subscribers.get(event.event_type, [])):
            handler(event)

    def replay(self, event_history: Optional[List[DomainEvent]] = None) -> None:
        for event in event_history or self._history:
            for handler in list(self._subscribers.get(event.event_type, [])):
                handler(event)

    def log(self, event: DomainEvent) -> None:
        self._history.append(event)
