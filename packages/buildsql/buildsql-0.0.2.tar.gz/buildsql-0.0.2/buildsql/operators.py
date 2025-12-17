"""Defines SQL logical operators for building conditions."""

from __future__ import annotations

from collections.abc import Sequence

from .base import StrOrTerminal, get_value
from .utils import join_conditions


def and_(condition_1: StrOrTerminal, *conditions: StrOrTerminal) -> StrOrTerminal:
    """Create an AND condition for SQL statements.

    TODO: link to docs.
    TODO: example usage
    """
    return join_conditions("and", condition_1, *conditions)


def or_(condition_1: StrOrTerminal, *conditions: StrOrTerminal) -> StrOrTerminal:
    """Create an OR condition for SQL statements.

    TODO: link to docs.
    TODO: example usage
    """
    return join_conditions("or", condition_1, *conditions)


def in_(column: StrOrTerminal, values: Sequence[StrOrTerminal]) -> StrOrTerminal:
    """Create an IN condition for SQL statements.

    TODO: link to docs.
    TODO: example usage
    """
    vals = ", ".join(get_value(val) for val in values)
    return f"{get_value(column)} in ({vals})"


def eq(column: StrOrTerminal, value: StrOrTerminal) -> StrOrTerminal:
    """Create an equality condition for SQL statements.

    TODO: link to docs.
    TODO: example usage
    """
    return f"{get_value(column)} = {get_value(value)}"
