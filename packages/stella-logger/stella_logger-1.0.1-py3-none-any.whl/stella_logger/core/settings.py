from __future__ import annotations

from pydantic import BaseModel, Field


class StellaCoreSettings(BaseModel):
    include_service_name: bool = Field(default=True)
    include_service_version: bool = Field(default=True)
    service_name: str | None = Field(default=None)
    service_version: str | None = Field(default=None)
    structured_message: bool = Field(default=True)
    payload_attr_name: str = Field(default="")
    flat_collision_prefix: str = Field(default="stella_")
    drop_message_in_flat_extra: bool = Field(default=True)

    model_config = {"frozen": True}
