from __future__ import annotations

import string
from typing import Any, Mapping


class SafeFormatter(string.Formatter):
    """Formatter that leaves unknown placeholders untouched."""

    def get_value(self, key, args, kwargs):  # type: ignore[override]
        if isinstance(key, str):
            if key in kwargs:
                return kwargs[key]
            return "{" + key + "}"
        return super().get_value(key, args, kwargs)

    def format_from_mapping(self, template: str, mapping: Mapping[str, Any]) -> str:
        return self.format(template, **mapping)
