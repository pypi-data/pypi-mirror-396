from .base import StrOrTerminal, get_value
from collections.abc import Sequence


def wrap_parentheses(value: StrOrTerminal) -> StrOrTerminal:
    val = get_value(value)

    if val.startswith("(") and val.endswith(")"):
        return val

    return f"({val})"


def join_conditions(
    operator: str,
    condition_1: StrOrTerminal,
    *conditions: StrOrTerminal,
) -> StrOrTerminal:
    values = (get_value(cond) for cond in [condition_1, *conditions])
    joined = f" {operator} ".join(values)
    return wrap_parentheses(joined)


def join_with_commas(items: Sequence[StrOrTerminal]) -> StrOrTerminal:
    values = (get_value(item) for item in items)
    joined = ", ".join(values)
    return joined
