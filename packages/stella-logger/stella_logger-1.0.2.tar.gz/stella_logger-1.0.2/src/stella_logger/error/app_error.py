from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class LogEventError(Exception):
    """
    User-defined exception carrying a Stella log event key and context.

    Attributes:
        key: event_key associated with a LogDefinition.
        context: Payload fields to log alongside the event.
        cause: Optional underlying exception to chain.
    """

    key: str
    context: Dict[str, Any]
    cause: Optional[Exception] = None

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"LogEventError(key={self.key}, context={self.context}, cause={self.cause})"
