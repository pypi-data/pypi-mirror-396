from __future__ import annotations

import logging
from typing import Any, Dict

RESERVED_LOG_RECORD_ATTRS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    "message",
    "asctime",
}


def apply_collision_prefix(data: Dict[str, Any], prefix: str) -> Dict[str, Any]:
    """Prefix keys that collide with LogRecord reserved attributes."""
    prefixed: Dict[str, Any] = {}
    for key, value in data.items():
        target_key = f"{prefix}{key}" if key in RESERVED_LOG_RECORD_ATTRS else key
        prefixed[target_key] = value
    return prefixed
