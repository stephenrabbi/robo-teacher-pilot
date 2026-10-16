"""Synthetic offline queue coordinator. No live browser integration.

The caller persists the queue independently; this pure coordinator returns the
updated queue and never drops an event merely because transport failed.
"""
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class PendingEvent:
    event_id: str
    payload: dict
    attempts: int = 0

@dataclass(frozen=True)
class SyncResult:
    remaining: tuple
    acknowledged: tuple
    failed: bool

def synchronize(pending: tuple[PendingEvent, ...], submit: Callable[[dict], bool]) -> SyncResult:
    """Stop at the first uncertain failure, retaining that and later events."""
    if not isinstance(pending, tuple) or any(not isinstance(x, PendingEvent) for x in pending):
        raise ValueError("Invalid pending queue")
    acknowledged = []
    for index, item in enumerate(pending):
        if item.payload.get("event_id") != item.event_id:
            raise ValueError("Queue identity mismatch")
        try:
            response = submit(dict(item.payload))
            # Both a newly inserted event (True) and an idempotently existing
            # identical event (False) are accepted acknowledgements.
            if type(response) is not bool:
                raise ConnectionError("Missing definitive acknowledgement")
        except (ConnectionError, TimeoutError, OSError):
            retry = PendingEvent(item.event_id, dict(item.payload), item.attempts + 1)
            return SyncResult((retry,) + pending[index + 1:], tuple(acknowledged), True)
        acknowledged.append(item.event_id)
    return SyncResult((), tuple(acknowledged), False)
