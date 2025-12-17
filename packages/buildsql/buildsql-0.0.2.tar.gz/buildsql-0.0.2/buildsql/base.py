"""Defines the base classes and utilities for building SQL statements."""

from __future__ import annotations

from typing import Literal, Optional


class Buildable:
    """Base class for SQL statement builders."""

    def build(self) -> str:
        """Create the final SQL statement."""
        raise NotImplementedError()


def get_value(value: int | str | Buildable) -> str:
    """Build the sql query if needed, otherwise return static value."""
    if isinstance(value, Buildable):
        return value.build()

    return str(value)


class Terminal(Buildable):
    """Base class for SQL statement terminals."""

    def __init__(self, parts: Optional[list[StrOrBuildable]] = None) -> None:
        if parts is None:
            parts = []

        self._parts = parts

    def build(self) -> str:
        """Create the final SQL statement."""
        return "\n".join(get_value(part) for part in self._parts)


StrOrBuildable = str | Buildable
IntOrBuildable = int | Buildable

StrOrTerminal = str | Terminal
IntOrTerminal = int | Terminal
BoolOrTerminal = bool | Terminal

OrderDirection = Literal["asc", "desc"]
BaseOrderT = StrOrTerminal | tuple[StrOrTerminal, OrderDirection]
