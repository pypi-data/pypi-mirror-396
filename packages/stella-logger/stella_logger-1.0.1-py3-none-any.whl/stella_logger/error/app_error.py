from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class LogEventError(Exception):
    key: str
    context: Dict[str, Any]
    cause: Optional[Exception] = None

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"LogEventError(key={self.key}, context={self.context}, cause={self.cause})"
