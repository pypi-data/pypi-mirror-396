from __future__ import annotations

import logging
from enum import Enum


class StellaSeverity(str, Enum):
    """Severity levels used by StellaLogger, aligned with stdlib logging."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

    def to_logging_level(self) -> int:
        """
        Convert this severity to the corresponding stdlib `logging` level number.

        Returns:
            int: The numeric logging level (e.g., logging.INFO).
        """
        level_map = {
            StellaSeverity.DEBUG: logging.DEBUG,
            StellaSeverity.INFO: logging.INFO,
            StellaSeverity.WARNING: logging.WARNING,
            StellaSeverity.ERROR: logging.ERROR,
            StellaSeverity.CRITICAL: logging.CRITICAL,
        }
        return level_map[self]
