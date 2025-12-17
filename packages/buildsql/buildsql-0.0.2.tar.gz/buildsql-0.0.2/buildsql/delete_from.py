"""Defines the DELETE FROM statement and its clauses."""

from __future__ import annotations

from typing import Optional

from .base import Buildable, StrOrBuildable, StrOrTerminal, Terminal, get_value
from .utils import join_with_commas


class Returning(Buildable):
    """Represents a RETURNING clause of a DELETE statement."""

    def __init__(self, *returning: StrOrTerminal) -> None:
        self._returning = returning

    def build(self) -> str:
        """Create a RETURNING clause."""
        returning = join_with_commas(self._returning)
        return f"returning {returning}"


class ReturningAble(Terminal):
    """Defines the RETURNING clause of a DELETE statement."""

    # TODO: have `return_all` as shortcut for `returning("*")`?

    def returning(self, *returning: StrOrTerminal) -> Terminal:
        """Specify which columns to return after the DELETE.

        TODO: link to docs.
        TODO: example usage
        """
        return Terminal([*self._parts, Returning(*returning)])


class Where(Buildable):
    """Represents a WHERE clause of a DELETE statement."""

    def __init__(self, condition: StrOrTerminal) -> None:
        self._condition = condition

    def build(self) -> str:
        """Create a WHERE clause."""
        where = get_value(self._condition)
        return f"where {where}"


class Whereable(ReturningAble):
    """Defines the WHERE clause of a DELETE statement."""

    def where(self, condition: StrOrTerminal) -> ReturningAble:
        # TODO: can this inherit from MustWhereable to not repeat?
        """Determine which rows to delete.

        TODO: link to docs.
        TODO: example usage
        """
        return ReturningAble([*self._parts, Where(condition)])


class MustWhereable:
    """Defines a DELETE statement that requires a WHERE clause."""

    def __init__(self, parts: Optional[list[StrOrBuildable]] = None) -> None:
        if parts is None:
            parts = []

        self._parts = parts

    def where(self, condition: StrOrTerminal) -> ReturningAble:
        """Determine which rows to delete.

        TODO: link to docs.
        TODO: example usage
        """
        return ReturningAble([*self._parts, Where(condition)])


class Using(Buildable):
    """Represents a USING clause of a DELETE statement."""

    def __init__(self, using_clause: StrOrTerminal) -> None:
        self._using_clause = using_clause

    def build(self) -> str:
        """Create a USING clause."""
        using_clause = get_value(self._using_clause)
        return f"using {using_clause}"


class Usingable(Whereable):
    """Defines the USING clause of a DELETE statement."""

    def __init__(self, delete_from: DeleteFrom) -> None:
        self._parts = [delete_from]

    def using(self, using_clause: StrOrTerminal) -> MustWhereable:
        """Specify another table to delete from in a DELETE statement.

        TODO: link to docs.
        TODO: example usage
        """
        return MustWhereable([*self._parts, Using(using_clause)])


class DeleteFrom(Buildable):
    """Represents a DELETE FROM clause of a DELETE statement."""

    def __init__(self, table_name: str) -> None:
        self._table_name = table_name

    def build(self) -> str:
        """Create a DELETE FROM clause."""
        return f"delete from {self._table_name}"


def delete_from(table_name: str) -> Usingable:
    """TODO: link to docs. TODO: example usage."""
    return Usingable(DeleteFrom(table_name))
