from __future__ import annotations

from typing import Dict, Iterable

from .definition import LogDefinition


class LogRegistry:
    def __init__(self, definitions: Iterable[LogDefinition]):
        self._by_key: Dict[str, LogDefinition] = {}
        self._by_code: Dict[int, LogDefinition] = {}

        for definition in definitions:
            if definition.key in self._by_key:
                raise ValueError(f"Duplicate log key detected: {definition.key}")
            if definition.numeric in self._by_code:
                raise ValueError(f"Duplicate log numeric detected: {definition.numeric}")
            self._by_key[definition.key] = definition
            self._by_code[definition.numeric] = definition

    def get(self, key: str) -> LogDefinition:
        if key not in self._by_key:
            raise KeyError(f"LogDefinition not found for key: {key}")
        return self._by_key[key]

    def get_by_code(self, numeric: int) -> LogDefinition:
        if numeric not in self._by_code:
            raise KeyError(f"LogDefinition not found for numeric: {numeric}")
        return self._by_code[numeric]
