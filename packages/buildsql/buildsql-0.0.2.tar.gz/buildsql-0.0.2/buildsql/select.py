"""Defines the SELECT statement and its clauses."""

from __future__ import annotations

from typing import Literal, Optional

from .base import (
    BaseOrderT,
    Buildable,
    IntOrTerminal,
    StrOrBuildable,
    StrOrTerminal,
    Terminal,
    get_value,
)
from .utils import join_with_commas

FetchDirection = Literal["first", "next"]
FetchTieType = Literal["only", "with ties"]

# todo: need to know if limit(1) or fetch(1) to get return types?


class Fetch(Buildable):
    """Represents a FETCH clause of a SELECT statement."""

    def __init__(
        self,
        direction: FetchDirection,
        fetch: IntOrTerminal,
        tie: FetchTieType,
    ) -> None:
        self._direction = direction
        self._fetch = fetch
        self._tie = tie

    def build(self) -> str:
        """Create a FETCH clause."""
        fetch = get_value(self._fetch)

        if fetch == 1 and self._tie == "only":
            return f"fetch {self._direction} row only"

        return f"fetch {self._direction} {fetch} rows {self._tie}"


class Fetchable(Terminal):
    """Defines the FETCH clause of a SELECT statement."""

    def fetch(
        self,
        direction: FetchDirection,
        fetch: IntOrTerminal,
        tie: FetchTieType,
    ) -> Terminal:
        """Define the FETCH clause.

        TODO: link to docs.
        TODO: example usage
        """
        return Terminal([*self._parts, Fetch(direction, fetch, tie)])


class Offset(Buildable):
    """Represents an OFFSET clause of a SELECT statement."""

    def __init__(self, offset: IntOrTerminal) -> None:
        self._offset = offset

    def build(self) -> str:
        """Create an OFFSET clause."""
        offset = get_value(self._offset)

        if offset == 0:
            return "offset 1 row"

        return f"offset {offset} rows"


class Offsetable(Fetchable):
    """Defines the OFFSET clause of a SELECT statement."""

    def offset(self, offset: IntOrTerminal) -> Fetchable:
        """Define the OFFSET clause.

        TODO: link to docs.
        TODO: example usage
        """
        return Fetchable([*self._parts, Offset(offset)])


class Limit(Buildable):
    """Represents a LIMIT clause of a SELECT statement."""

    def __init__(self, limit: IntOrTerminal) -> None:
        self._limit = limit

    def build(self) -> str:
        """Create a LIMIT clause."""
        limit = get_value(self._limit)
        return f"limit {limit}"


class Limitable(Offsetable):
    """Defines the LIMIT clause of a SELECT statement."""

    # TODO: required 1 or optional 1 (find)
    # limit 2 - only 1... (get)
    def limit(self, limit: IntOrTerminal) -> Offsetable:
        """Define the LIMIT clause.

        TODO: link to docs.
        TODO: example usage
        """
        return Offsetable([*self._parts, Limit(limit)])


class Order(Buildable):
    """Represents an ORDER BY clause of a SELECT statement."""

    def __init__(self, col_1: BaseOrderT, *columns: BaseOrderT) -> None:
        self._columns = (col_1, *columns)

    def build(self) -> str:
        """Create an ORDER BY clause."""
        cols: list[str] = []

        for col in self._columns:
            if isinstance(col, tuple):
                column, direction = col
                cols.append(f"{get_value(column)} {direction}")
            else:
                cols.append(get_value(col))

        return f"order by {join_with_commas(cols)}"


class Orderable(Limitable):
    """Defines the ORDER BY clause of a SELECT statement."""

    def order_by(self, col_1: BaseOrderT, *columns: BaseOrderT) -> Limitable:
        """Define the ORDER BY clause.

        TODO: link to docs.
        TODO: example usage
        """
        return Limitable([*self._parts, Order(col_1, *columns)])


class Having(Buildable):
    """Represents a HAVING clause of a SELECT statement."""

    def __init__(self, condition: StrOrTerminal) -> None:
        self._condition = condition

    def build(self) -> str:
        """Create a HAVING clause."""
        having = get_value(self._condition)
        return f"having {having}"


class Havingable(Orderable):
    """Defines the HAVING clause of a SELECT statement."""

    def having(self, condition: StrOrTerminal) -> Orderable:
        """Define the HAVING clause.

        TODO: link to docs.
        TODO: example usage
        """
        return Orderable([*self._parts, Having(condition)])


class GroupBy(Buildable):
    """Represents a GROUP BY clause of a SELECT statement."""

    def __init__(self, *columns: StrOrTerminal) -> None:
        self._columns = columns

    def build(self) -> str:
        """Create a GROUP BY clause."""
        return f"group by {join_with_commas(self._columns)}"


class GroupByable(Orderable):
    """Defines the GROUP BY clause of a SELECT statement."""

    def group_by(self, col_1: StrOrTerminal, *columns: StrOrTerminal) -> Havingable:
        """Define the GROUP BY clause.

        TODO: link to docs.
        TODO: example usage
        """
        return Havingable([*self._parts, GroupBy(col_1, *columns)])

    # TODO: group_by_rollup, group_by_cube, group_by_grouping_sets


class Where(Buildable):
    """Represents a WHERE clause of a SELECT statement."""

    def __init__(self, condition: StrOrTerminal) -> None:
        self._condition = condition

    def build(self) -> str:
        """Create a WHERE clause."""
        where = get_value(self._condition)
        return f"where {where}"


class Whereable(GroupByable):
    """Defines the WHERE clause of a SELECT statement."""

    def where(self, condition: StrOrTerminal) -> GroupByable:
        """Determine which rows to select.

        TODO: link to docs.
        TODO: example usage
        """
        return GroupByable([*self._parts, Where(condition)])


#
# TODO: JOINS
#


class BaseJoin(Buildable):
    """Represents a JOIN clause of a SELECT statement."""

    def __init__(
        self,
        join_type: str,
        table: StrOrTerminal,
        *,
        on: StrOrTerminal,
    ) -> None:
        self._join_type = join_type
        self._table = table
        self._on = on

    def build(self) -> str:
        """Create a JOIN clause."""
        table = get_value(self._table)
        on = get_value(self._on)
        return f"{self._join_type} join {table} on {on}"


class LeftJoin(BaseJoin):
    """Represents a LEFT JOIN clause of a SELECT statement."""

    def __init__(self, table: StrOrTerminal, *, on: StrOrTerminal) -> None:
        super().__init__("left", table, on=on)


class RightJoin(BaseJoin):
    """Represents a RIGHT JOIN clause of a SELECT statement."""

    def __init__(self, table: StrOrTerminal, *, on: StrOrTerminal) -> None:
        super().__init__("right", table, on=on)


class InnerJoin(BaseJoin):
    """Represents an INNER JOIN clause of a SELECT statement."""

    def __init__(self, table: StrOrTerminal, *, on: StrOrTerminal) -> None:
        super().__init__("inner", table, on=on)


class FullJoin(BaseJoin):
    """Represents a FULL JOIN clause of a SELECT statement."""

    def __init__(self, table: StrOrTerminal, *, on: StrOrTerminal) -> None:
        super().__init__("full", table, on=on)


class LateralJoin(BaseJoin):
    """Represents a LATERAL JOIN clause of a SELECT statement."""

    def __init__(self, table: StrOrTerminal, *, on: StrOrTerminal) -> None:
        super().__init__("lateral", table, on=on)


class CrossJoin(Buildable):
    """Represents a CROSS JOIN clause of a SELECT statement."""

    def __init__(self, table: StrOrTerminal) -> None:
        self._table = table

    def build(self) -> str:
        """Create a CROSS JOIN clause."""
        table = get_value(self._table)
        return f"cross join {table}"


# TODO: natural_join


class BaseJoinable(Whereable):
    """Defines JOIN clauses of a SELECT statement."""

    def left_join(self, table: StrOrTerminal, *, on: StrOrTerminal) -> BaseJoinable:
        """Specify a LEFT JOIN clause.

        TODO: link to docs.
        TODO: example usage
        """
        return BaseJoinable([*self._parts, LeftJoin(table, on=on)])

    def right_join(self, table: StrOrTerminal, *, on: StrOrTerminal) -> BaseJoinable:
        """Specify a RIGHT JOIN clause.

        TODO: link to docs.
        TODO: example usage
        """
        return BaseJoinable([*self._parts, RightJoin(table, on=on)])

    def inner_join(self, table: StrOrTerminal, *, on: StrOrTerminal) -> BaseJoinable:
        """Specify an INNER JOIN clause.

        TODO: link to docs.
        TODO: example usage
        """
        return BaseJoinable([*self._parts, InnerJoin(table, on=on)])

    def full_join(self, table: StrOrTerminal, *, on: StrOrTerminal) -> BaseJoinable:
        """Specify a FULL JOIN clause.

        TODO: link to docs.
        TODO: example usage
        """
        return BaseJoinable([*self._parts, FullJoin(table, on=on)])

    def cross_join(self, table: StrOrTerminal) -> BaseJoinable:
        """Specify a CROSS JOIN clause.

        TODO: link to docs.
        TODO: example usage
        """
        return BaseJoinable([*self._parts, CrossJoin(table)])

    def lateral_join(self, table: StrOrTerminal, *, on: StrOrTerminal) -> BaseJoinable:
        """Specify a LATERAL JOIN clause.

        TODO: link to docs.
        TODO: example usage
        """
        return BaseJoinable([*self._parts, LateralJoin(table, on=on)])


class From(Buildable):
    """Represents a FROM clause of a SELECT statement."""

    def __init__(self, table: StrOrTerminal) -> None:
        self._table = table

    def build(self) -> str:
        """Create a FROM clause."""
        table = get_value(self._table)
        return f"from {table}"


class Fromable(Terminal):
    """Defines the FROM clause of a SELECT statement."""

    def __init__(self, select: Select) -> None:
        self._parts = [select]

    def from_(self, table: StrOrTerminal) -> BaseJoinable:
        # TODO: can this inherit from MustFromable to not repeat?
        """Specify the table to select from.

        TODO: link to docs. TODO: example usage
        """
        return BaseJoinable([*self._parts, From(table)])


class MustFromable:
    """Defines a SELECT statement that requires a FROM clause."""

    def __init__(self, parts: Optional[list[StrOrBuildable]] = None) -> None:
        if parts is None:
            parts = []

        self._parts = parts

    def from_(self, table: StrOrTerminal) -> BaseJoinable:
        """Specify the table to select from.

        TODO: link to docs. TODO: example usage
        """
        return BaseJoinable([*self._parts, From(table)])


class SelectDistinctOnable(Fromable):
    """Defines a SELECT DISTINCT ON clause of a SELECT statement."""

    def __init__(self, select_distinct: SelectDistinct) -> None:
        self._parts = [select_distinct]
        self._select_distinct = select_distinct

    def on(self, on_col_1: StrOrTerminal, *on_columns: StrOrTerminal) -> MustFromable:
        """Specify the columns for the DISTINCT ON clause.

        TODO: link to docs. TODO: example usage
        """
        return MustFromable(
            [
                SelectDistinctOn(
                    [on_col_1, *on_columns],
                    self._select_distinct._columns,
                )
            ]
        )


class Select(Buildable):
    """Represents a SELECT clause of a SELECT statement."""

    # TODO: could also be numbers etc...
    def __init__(self, columns: StrOrTerminal) -> None:
        self._columns = columns

    def build(self) -> str:
        """Create a SELECT clause."""
        return f"select {join_with_commas(self._columns)}"


class SelectDistinct(Buildable):
    """Represents a SELECT DISTINCT clause of a SELECT statement."""

    def __init__(self, *columns: StrOrTerminal) -> None:
        self._columns = columns

    def build(self) -> str:
        """Create a SELECT DISTINCT clause."""
        return f"select distinct {join_with_commas(self._columns)}"


class SelectDistinctOn(Buildable):
    """Represents a SELECT DISTINCT ON clause of a SELECT statement."""

    def __init__(
        self,
        on_columns: list[StrOrTerminal],
        columns: StrOrTerminal,
    ) -> None:
        self._on_columns = on_columns
        self._columns = columns

    def build(self) -> str:
        """Create a SELECT DISTINCT ON clause."""
        return f"select distinct on ({join_with_commas(self._on_columns)}) {join_with_commas(self._columns)}"


# select_all for shortcut for select("*")?
def select(col_1: StrOrTerminal, *columns: StrOrTerminal) -> Fromable:
    """TODO: link to docs. TODO: example usage."""
    return Fromable(Select(col_1, *columns))


def select_distinct(
    col_1: StrOrTerminal,
    *columns: StrOrTerminal,
) -> SelectDistinctOnable:
    """TODO: link to docs. TODO: example usage.

    TODO: explain when to use DISTINCT vs DISTINCT ON.
    """
    return SelectDistinctOnable(SelectDistinct(col_1, *columns))


# TODO: https://www.postgresql.org/docs/current/sql-select.html
#
# * window
# * union / intersect / except
# * CTEs
# * for
# * gen_random_uuid(), now(), current_date, current_time, current_timestamp, ...
# * Operators: @>, <@, ||, ->>, ?, ...
