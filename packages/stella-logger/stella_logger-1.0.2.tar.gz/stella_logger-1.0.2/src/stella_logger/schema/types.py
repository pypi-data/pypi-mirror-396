from __future__ import annotations

from enum import Enum
from typing import Literal

SeverityLiteral = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class LogKind(str, Enum):
    """Logical kind of log event (event vs error)."""

    EVENT = "EVENT"
    ERROR = "ERROR"
