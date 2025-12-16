from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional

from .reserved import apply_collision_prefix
from .severity import StellaSeverity
from .settings import StellaCoreSettings


class StellaCoreLogger:
    def __init__(
        self,
        settings: StellaCoreSettings,
        base_logger: Optional[logging.Logger] = None,
    ) -> None:
        self.settings = settings
        self.base_logger = base_logger or logging.getLogger("stella")

    def log(
        self,
        payload: Dict[str, Any],
        severity: StellaSeverity | str,
        exc_info: Any = None,
    ) -> None:
        level = self._to_level(severity)
        working_payload = dict(payload)

        if (
            self.settings.include_service_name
            and self.settings.service_name
            and "service_name" not in working_payload
        ):
            working_payload["service_name"] = self.settings.service_name
        if (
            self.settings.include_service_version
            and self.settings.service_version
            and "service_version" not in working_payload
        ):
            working_payload["service_version"] = self.settings.service_version

        msg: str
        extra: Optional[Dict[str, Any]]

        if self.settings.structured_message:
            msg = json.dumps(working_payload, ensure_ascii=False)
            extra = None
        elif self.settings.payload_attr_name:
            msg = str(working_payload.get("message", ""))
            extra = {self.settings.payload_attr_name: working_payload}
        else:
            msg = str(working_payload.get("message", ""))
            extra = apply_collision_prefix(
                working_payload,
                prefix=self.settings.flat_collision_prefix,
            )
            if self.settings.drop_message_in_flat_extra:
                extra.pop("message", None)

        self.base_logger.log(level, msg, extra=extra, exc_info=exc_info)

    @staticmethod
    def _to_level(severity: StellaSeverity | str) -> int:
        if isinstance(severity, StellaSeverity):
            return severity.to_logging_level()
        return StellaSeverity(severity).to_logging_level()
