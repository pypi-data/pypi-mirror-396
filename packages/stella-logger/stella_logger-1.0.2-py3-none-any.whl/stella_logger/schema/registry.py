from __future__ import annotations

from typing import Dict, Iterable

from .definition import LogDefinition


class LogRegistry:
    """Registry enforcing unique log definitions and providing lookup by key or code."""

    def __init__(self, definitions: Iterable[LogDefinition]):
        self._by_key: Dict[str, LogDefinition] = {}
        self._by_code: Dict[int, LogDefinition] = {}

        for definition in definitions:
            if definition.event_key in self._by_key:
                raise ValueError(f"Duplicate log key detected: {definition.event_key}")
            if definition.event_code in self._by_code:
                raise ValueError(f"Duplicate log numeric detected: {definition.event_code}")
            self._by_key[definition.event_key] = definition
            self._by_code[definition.event_code] = definition

    def get(self, key: str) -> LogDefinition:
        """
        Retrieve a LogDefinition by event_key.

        Args:
            key: Event key to look up.

        Raises:
            KeyError: If the key is not registered.

        Returns:
            LogDefinition: The matching definition.
        """
        if key not in self._by_key:
            raise KeyError(f"LogDefinition not found for key: {key}")
        return self._by_key[key]

    def get_by_code(self, numeric: int) -> LogDefinition:
        """
        Retrieve a LogDefinition by event_code.

        Args:
            numeric: Event code to look up.

        Raises:
            KeyError: If the code is not registered.

        Returns:
            LogDefinition: The matching definition.
        """
        if numeric not in self._by_code:
            raise KeyError(f"LogDefinition not found for numeric: {numeric}")
        return self._by_code[numeric]
