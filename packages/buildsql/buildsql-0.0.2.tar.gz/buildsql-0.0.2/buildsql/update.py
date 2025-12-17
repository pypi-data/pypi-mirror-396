"""Represents an UPDATE statement."""

from __future__ import annotations

from .base import (
    Buildable,
    StrOrTerminal,
    Terminal,
    get_value,
)
from .utils import join_with_commas


class Returning(Buildable):
    """Represents a RETURNING clause of an UPDATE statement."""

    def __init__(self, *returning: StrOrTerminal) -> None:
        self._returning = returning

    def build(self) -> str:
        """Create a RETURNING clause."""
        returning = join_with_commas(self._returning)
        return f"returning {returning}"


class ReturningAble(Terminal):
    """Defines the RETURNING clause of an UPDATE statement."""

    # TODO: have `return_all` as shortcut for `returning("*")`?

    def returning(self, col_1: StrOrTerminal, *columns: StrOrTerminal) -> Terminal:
        """Specify which columns to return after the UPDATE.

        TODO: link to docs.
        TODO: example usage Show returning updated values vs original values.
        """
        return Terminal([*self._parts, Returning(col_1, *columns)])


class Where(Buildable):
    """Represents a WHERE clause of an UPDATE statement."""

    def __init__(self, condition: StrOrTerminal) -> None:
        self._condition = condition

    def build(self) -> str:
        """Create a WHERE clause."""
        where = get_value(self._condition)
        return f"where {where}"


class Whereable(ReturningAble):
    """Defines the WHERE clause of an UPDATE statement."""

    def where(self, condition: StrOrTerminal) -> ReturningAble:
        """Determine which rows to update.

        TODO: link to docs.
        TODO: example usage
        """
        return ReturningAble([*self._parts, Where(condition)])


class From(Buildable):
    """Represents a FROM clause of an UPDATE statement."""

    def __init__(self, table: StrOrTerminal) -> None:
        self._table = table

    def build(self) -> str:
        """Create a FROM clause."""
        table = get_value(self._table)
        return f"from {table}"


class Fromeable(Whereable):
    """Defines the FROM clause of an UPDATE statement."""

    def from_(self, table: StrOrTerminal) -> Whereable:
        """Use another table to update the target table from.

        TODO: link to docs.
        TODO: example usage
        """
        return Whereable([*self._parts, From(table)])


class Set(Buildable):
    """Represents a SET clause of an UPDATE statement."""

    def __init__(self, *set_clause: StrOrTerminal) -> None:
        self._set_clause = set_clause

    def build(self) -> str:
        """Create a SET clause."""
        set_clause = join_with_commas(self._set_clause)
        return f"set {set_clause}"


class Setable:
    """Defines the SET clause of an UPDATE statement."""

    def __init__(self, update: Update) -> None:
        self._parts = [update]

    def set(self, *set_clause: StrOrTerminal) -> Fromeable:
        """Define which columns to update.

        TODO: link to docs.
        TODO: example usage
        """
        return Fromeable([*self._parts, Set(*set_clause)])


class Update(Buildable):
    """Represents an UPDATE clause."""

    def __init__(self, table_name: str) -> None:
        self._table_name = table_name

    def build(self) -> str:
        """Create an UPDATE clause."""
        return f"update {self._table_name}"


def update(table_name: str) -> Setable:
    """TODO: link to docs. TODO: example usage."""
    return Setable(Update(table_name))
