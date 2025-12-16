from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel

from ..core import StellaCoreLogger
from ..schema import LogDefinition, LogRegistry, SafeFormatter
from ..schema.types import LogKind
from ..error import LogEventError


class StellaLogger:
    def __init__(self, core: StellaCoreLogger, registry: LogRegistry):
        self.core = core
        self.registry = registry
        self._formatter = SafeFormatter()

    def log_event(
        self,
        key: str,
        extra: Optional[Dict[str, Any]] = None,
        exc: Any = None,
    ) -> None:
        definition = self.registry.get(key)
        self._log_with_definition(definition, extra=extra, exc=exc)

    def log_error(
        self,
        key: str,
        extra: Optional[Dict[str, Any]] = None,
        exc: Any = None,
    ) -> None:
        definition = self.registry.get(key)
        if definition.kind != LogKind.ERROR:
            raise ValueError("log_error can only be used with LogKind.ERROR definitions")
        self._log_with_definition(definition, extra=extra, exc=exc)

    def log_from_error(self, err: LogEventError) -> None:
        self.log_event(err.key, extra=err.context, exc=err.cause)

    def _log_with_definition(
        self,
        definition: LogDefinition,
        extra: Optional[Dict[str, Any]],
        exc: Any = None,
    ) -> None:
        extra_payload = dict(extra or {})
        if "message" in extra_payload:
            raise ValueError("Overriding message is not allowed")

        template_payload = dict(extra_payload)
        rendered_message = self._formatter.format_from_mapping(
            definition.message_template,
            template_payload,
        )

        validation_input = dict(extra_payload)
        if definition.include_message_in_extra:
            validation_input["message"] = rendered_message

        payload_extra: Dict[str, Any]
        if definition.schema_model:
            payload_extra = self._validate(definition.schema_model, validation_input)
        else:
            payload_extra = validation_input

        message_value = payload_extra.get("message", rendered_message)

        payload: Dict[str, Any] = {
            "event_key": definition.key,
            "event_code": definition.numeric,
            "message": message_value,
            "severity": definition.severity.value,
            "kind": definition.kind.value,
        }
        if definition.category is not None:
            payload["category"] = definition.category

        payload.update(payload_extra)

        self.core.log(payload, severity=definition.severity, exc_info=exc)

    @staticmethod
    def _validate(model: type[BaseModel], data: Dict[str, Any]) -> Dict[str, Any]:
        validated = model.model_validate(data)
        return validated.model_dump()
