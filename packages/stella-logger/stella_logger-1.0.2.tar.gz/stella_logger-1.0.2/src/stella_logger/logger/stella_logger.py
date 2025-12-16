from __future__ import annotations

from typing import Any, Dict, Optional

from pydantic import BaseModel

from ..core import StellaCoreLogger
from ..error import LogEventError
from ..schema import LogDefinition, LogRegistry, SafeFormatter
from ..schema.types import LogKind


class StellaLogger:
    """
    High-level logger that builds, validates, and emits structured events.

    It enforces LogDefinition rules (template rendering, schema validation, reserved message)
    and delegates emission to `StellaCoreLogger`.
    """

    def __init__(self, core: StellaCoreLogger, registry: LogRegistry):
        """
        Args:
            core: Core adapter responsible for output formatting and emission.
            registry: Registry containing available log definitions.
        """
        self.core = core
        self.registry = registry
        self._formatter = SafeFormatter()

    def log_event(
        self,
        key: str,
        extra: Optional[Dict[str, Any]] = None,
        exc: Any = None,
    ) -> None:
        """
        Log a non-error event by key.

        Args:
            key: event_key registered in LogRegistry.
            extra: Additional payload fields to validate and merge.
            exc: Optional exception info to forward to core logger.

        Raises:
            KeyError: If the key is not registered.
            ValueError: If extra attempts to override `message`.
            pydantic.ValidationError: If payload fails schema validation.
        """
        definition = self.registry.get(key)
        self._log_with_definition(definition, extra=extra, exc=exc)

    def log_error(
        self,
        key: str,
        extra: Optional[Dict[str, Any]] = None,
        exc: Any = None,
    ) -> None:
        """
        Log an error-kind event by key.

        Args:
            key: event_key registered in LogRegistry with event_kind=ERROR.
            extra: Additional payload fields to validate and merge.
            exc: Optional exception info to forward to core logger.

        Raises:
            ValueError: If the definition is not ERROR kind or message overridden.
            KeyError: If the key is not registered.
            pydantic.ValidationError: If payload fails schema validation.
        """
        definition = self.registry.get(key)
        if definition.event_kind != LogKind.ERROR:
            raise ValueError("log_error can only be used with LogKind.ERROR definitions")
        self._log_with_definition(definition, extra=extra, exc=exc)

    def log_from_error(self, err: LogEventError) -> None:
        """
        Log from a user-raised LogEventError.

        Args:
            err: Error containing event key, context, and cause.
        """
        self.log_event(err.key, extra=err.context, exc=err.cause)

    def _log_with_definition(
        self,
        definition: LogDefinition,
        extra: Optional[Dict[str, Any]],
        exc: Any = None,
    ) -> None:
        """
        Build, validate, and emit a payload using a specific LogDefinition.

        Args:
            definition: Log definition describing the event.
            extra: Payload fields supplied by caller.
            exc: Optional exception info to forward.

        Raises:
            ValueError: If caller tries to override message.
            pydantic.ValidationError: If schema validation fails.
        """
        extra_payload = dict(extra or {})
        if "message" in extra_payload:
            raise ValueError("Overriding message is not allowed")

        template_payload = {
            **{
                "event_key": definition.event_key,
                "event_code": definition.event_code,
                "event_severity": definition.event_severity.value,
                "event_kind": definition.event_kind.value,
                "event_category": definition.event_category,
            },
            **extra_payload,
        }
        rendered_message = self._formatter.format_from_mapping(
            definition.message_template,
            template_payload,
        )

        validation_input = dict(extra_payload)
        if definition.include_message_in_extra:
            validation_input["message"] = rendered_message

        payload_extra: Dict[str, Any]
        payload_extra = self._validate(definition.schema_model, validation_input)

        message_value = payload_extra.get("message", rendered_message)

        payload: Dict[str, Any] = {
            "event_key": definition.event_key,
            "event_code": definition.event_code,
            "message": message_value,
            "severity": definition.event_severity.value,
            "kind": definition.event_kind.value,
        }
        if definition.event_category is not None:
            payload["category"] = definition.event_category

        payload.update(payload_extra)

        if not definition.include_event_key_in_extra:
            payload.pop("event_key", None)
        if not definition.include_event_code_in_extra:
            payload.pop("event_code", None)
        if not definition.include_severity_in_extra:
            payload.pop("severity", None)
        if not definition.include_kind_in_extra:
            payload.pop("kind", None)
        if not definition.include_category_in_extra:
            payload.pop("category", None)

        self.core.log(payload, severity=definition.event_severity, exc_info=exc)

    @staticmethod
    def _validate(model: type[BaseModel], data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate payload data against a Pydantic model and return a dict.

        Args:
            model: Pydantic BaseModel subclass to validate against.
            data: Raw payload fields.

        Returns:
            Dict[str, Any]: Validated payload as plain dict.

        Raises:
            pydantic.ValidationError: If validation fails.
        """
        validated = model.model_validate(data)
        return validated.model_dump()
