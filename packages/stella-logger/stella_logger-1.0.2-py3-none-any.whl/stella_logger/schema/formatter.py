from __future__ import annotations

import string
from typing import Any, Mapping


class SafeFormatter(string.Formatter):
    """Formatter that leaves unknown placeholders untouched."""

    def get_value(self, key: int | str, args: tuple[Any, ...], kwargs: Mapping[str, Any]) -> Any:  # type: ignore[override]
        """Return value for key, or pass through `{key}` if missing."""
        if isinstance(key, str):
            if key in kwargs:
                return kwargs[key]
            return "{" + key + "}"
        return super().get_value(key, args, kwargs)

    def format_from_mapping(self, template: str, mapping: Mapping[str, Any]) -> str:
        """
        Format with a mapping while keeping unknown placeholders intact.

        Args:
            template: String containing placeholders.
            mapping: Values to apply to placeholders.

        Returns:
            Formatted string with missing placeholders preserved.
        """
        return self.format(template, **mapping)
