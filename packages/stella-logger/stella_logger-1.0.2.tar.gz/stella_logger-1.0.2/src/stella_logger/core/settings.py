from __future__ import annotations

from pydantic import BaseModel, Field


class StellaCoreSettings(BaseModel):
    """
    Settings controlling how `StellaCoreLogger` formats and emits payloads.

    Attributes:
        include_service_name: When True, inject `service_name` if provided.
        include_service_version: When True, inject `service_version` if provided.
        service_name: Optional service name to include in payloads.
        service_version: Optional service version to include in payloads.
        structured_message: If True, emit JSON string as message (JSON_MESSAGE mode).
        payload_attr_name: When non-empty, nest payload under this key in extra (NESTED_EXTRA).
        flat_collision_prefix: Prefix applied to LogRecord collisions in FLAT_EXTRA mode.
        drop_message_in_flat_extra: If True, remove `message` from extra in FLAT_EXTRA.
    """

    include_service_name: bool = Field(default=True)
    include_service_version: bool = Field(default=True)
    service_name: str | None = Field(default=None)
    service_version: str | None = Field(default=None)
    structured_message: bool = Field(default=True)
    payload_attr_name: str = Field(default="")
    flat_collision_prefix: str = Field(default="stella_")
    drop_message_in_flat_extra: bool = Field(default=True)

    model_config = {"frozen": True}
