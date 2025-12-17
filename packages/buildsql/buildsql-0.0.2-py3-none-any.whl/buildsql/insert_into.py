"""Defines the INSERT INTO statement and its clauses."""

from .base import (
    Buildable,
    StrOrTerminal,
    Terminal,
    get_value,
)
from .utils import join_with_commas


class Returning(Buildable):
    """Represents a RETURNING clause of an INSERT statement."""

    def __init__(self, *returning: StrOrTerminal) -> None:
        self._returning = returning

    def build(self) -> str:
        """Create a RETURNING clause."""
        returning = join_with_commas(self._returning)
        return f"returning {returning}"


class ReturningAble(Terminal):
    """Defines the RETURNING clause of an INSERT statement."""

    # TODO: have `return_all` as shortcut for `returning("*")`?

    def returning(self, *returning: StrOrTerminal) -> Terminal:
        """Specify which columns to return after the INSERT.

        TODO: show example with conflict vs no conflict.
        TODO: link to docs.
        TODO: example usage
        """
        return Terminal([*self._parts, Returning(*returning)])


class OnConflict(Buildable):
    """Represents an ON CONFLICT clause of an INSERT statement."""

    def __init__(self, on_conflict_clause: StrOrTerminal) -> None:
        self._on_conflict_clause = on_conflict_clause

    def build(self) -> str:
        """Create an ON CONFLICT clause."""
        on_conflict_clause = get_value(self._on_conflict_clause)
        return f"on conflict {on_conflict_clause}"


class OnConflictAble(ReturningAble):
    """Defines the ON CONFLICT clause of an INSERT statement."""

    # Future state??
    #
    # on_conflict("col_1", "col_2", where=..., on_constraint=...)
    # .do_nothing()
    #
    # on_conflict("col_1", "col_2", where=..., on_constraint=...)
    # .do_set_update("set a = 1", "set b = 2", where="...")
    #
    # what should be params vs new statement vs inner clauses??
    #
    # target = cols("a", "b").where().on_constraint("")
    #
    # action = do_update()
    # .set("a", "b")
    # .set("c", "d")
    # .where("...")
    #
    # on_conflict(target, action)
    #
    # have lambdas to make passing in easier?? idk

    def on_conflict(self, on_conflict_clause: StrOrTerminal) -> ReturningAble:
        """Specify the ON CONFLICT clause.

        Prefer `on_conflict_do_update_set` or `on_conflict_do_nothing` for convenience.

        TODO: link to docs.
        TODO: example usage
        """
        # this method isn't preferred over the other two, idk could remove
        return ReturningAble([*self._parts, OnConflict(on_conflict_clause)])


class Values(Buildable):
    """Represents a VALUES clause of an INSERT statement."""

    def __init__(self, *values_clause: StrOrTerminal) -> None:
        self._values_clause = values_clause

    def build(self) -> str:
        """Create a VALUES clause."""
        values_clause = join_with_commas(self._values_clause)
        return f"values ({values_clause})"


class ValuesAble:
    """Defines the VALUES clause of an INSERT statement."""

    def values(self, *values_clause: StrOrTerminal) -> OnConflictAble:
        """Specify the new values to insert.

        TODO: link to docs.
        TODO: example usage
        """
        return OnConflictAble([*self._parts, Values(*values_clause)])


class InsertInto(Buildable):
    """Defines the INSERT INTO clause of an INSERT statement."""

    def __init__(self, table: StrOrTerminal, column_names: list[str]) -> None:
        self._table = table
        self._column_names = column_names

    def build(self) -> str:
        """Create the INSERT INTO clause."""
        table = get_value(self._table)

        if len(self._column_names) == 0:
            return f"insert into {table}"

        columns = ", ".join(self._column_names)
        return f"insert into {table} ({columns})"


class Insertable(ValuesAble):
    """Represents an INSERT INTO statement."""

    def __init__(self, insert_into: InsertInto) -> None:
        self._parts = [insert_into]


def insert_into(table: StrOrTerminal, column_names: list[str]) -> Insertable:
    """TODO: link to docs. TODO: example usage."""
    # TODO: have `as`?
    return Insertable(InsertInto(table, column_names))


# columns...
# values ...
# returning ...

# on conflict...
