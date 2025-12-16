from __future__ import annotations

from typing import Type

from pydantic import BaseModel, Field, field_validator

from ..core.severity import StellaSeverity
from .types import LogKind

# Reserved keys that are injected automatically and cannot be declared in user schemas.
RESERVED_TEMPLATE_KEYS = {
    "event_key",
    "event_code",
    "event_severity",
    "event_kind",
    "event_category",
    "service_name",
    "service_version",
}


class LogDefinition(BaseModel):
    """
    Immutable definition of a log event.

    Attributes:
        event_key: Stable identifier for the event.
        event_code: Numeric code for the event.
        message_template: Template string used to render `message`.
        event_severity: Severity level for the event.
        event_kind: Logical kind (EVENT/ERROR).
        event_category: Optional category string.
        schema_model: Pydantic model to validate payloads (required).
        include_message_in_extra: If True, inject rendered `message` into validation payload.
        include_event_key_in_extra: If False, drop event_key from the emitted payload.
        include_event_code_in_extra: If False, drop event_code from the emitted payload.
        include_severity_in_extra: If False, drop severity from the emitted payload.
        include_kind_in_extra: If False, drop kind from the emitted payload.
        include_category_in_extra: If False, drop category from the emitted payload.
    """

    event_key: str
    event_code: int
    message_template: str
    event_severity: StellaSeverity
    event_kind: LogKind = Field(default=LogKind.EVENT)
    event_category: str | None = Field(default=None)
    schema_model: Type[BaseModel] = Field(...)
    include_message_in_extra: bool = Field(default=False)
    include_event_key_in_extra: bool = Field(default=True)
    include_event_code_in_extra: bool = Field(default=True)
    include_severity_in_extra: bool = Field(default=True)
    include_kind_in_extra: bool = Field(default=True)
    include_category_in_extra: bool = Field(default=True)

    model_config = {"frozen": True}

    @field_validator("schema_model")
    @classmethod
    def _check_schema_model(cls, value: Type[BaseModel]) -> Type[BaseModel]:
        """
        Ensure the schema_model is a BaseModel subclass and does not shadow reserved keys.

        Args:
            value: Pydantic model type to validate.

        Raises:
            TypeError: If schema_model is not a BaseModel subclass.
            ValueError: If schema_model declares reserved fields.
        """
        if not issubclass(value, BaseModel):
            msg = "schema_model must be a subclass of pydantic.BaseModel"
            raise TypeError(msg)
        model_fields = set(value.model_fields.keys())
        conflicts = model_fields & RESERVED_TEMPLATE_KEYS
        if conflicts:
            conflict_list = ", ".join(sorted(conflicts))
            msg = f"schema_model must not define reserved fields: {conflict_list}"
            raise ValueError(msg)
        return value
