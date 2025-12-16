from __future__ import annotations

from typing import Optional, Type

from pydantic import BaseModel, Field, field_validator

from .types import LogKind, SeverityLiteral
from ..core.severity import StellaSeverity


class LogDefinition(BaseModel):
    key: str
    numeric: int
    message_template: str
    severity: StellaSeverity
    kind: LogKind = Field(default=LogKind.EVENT)
    category: Optional[str] = Field(default=None)
    schema_model: Optional[Type[BaseModel]] = Field(default=None)
    include_message_in_extra: bool = Field(default=False)

    model_config = {"frozen": True}

    @field_validator("schema_model")
    @classmethod
    def _check_schema_model(cls, value: Optional[Type[BaseModel]]) -> Optional[Type[BaseModel]]:
        if value is None:
            return value
        if not issubclass(value, BaseModel):
            msg = "schema_model must be a subclass of pydantic.BaseModel"
            raise TypeError(msg)
        return value
