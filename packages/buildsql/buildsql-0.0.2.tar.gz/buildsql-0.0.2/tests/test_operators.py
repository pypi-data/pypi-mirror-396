from buildsql import and_, in_, or_


class TestAnd:

    def test_and_single_condition(self) -> None:
        cond = and_("a = 1")
        assert isinstance(cond, str)
        assert cond == "(a = 1)"

    def test_and_multiple_conditions(self) -> None:
        cond = and_("a = 1", "b = 2", "c = 3")
        assert isinstance(cond, str)
        assert cond == "(a = 1 and b = 2 and c = 3)"

    def test_with_expression(self) -> None:
        cond = and_("a = 1", or_("b = 2", "c = 3"))
        assert isinstance(cond, str)
        assert cond == "(a = 1 and (b = 2 or c = 3))"


class TestOr:

    def test_or_single_condition(self) -> None:
        cond = or_("a = 1")
        assert isinstance(cond, str)
        assert cond == "(a = 1)"

    def test_or_multiple_conditions(self) -> None:
        cond = or_("a = 1", "b = 2", "c = 3")
        assert isinstance(cond, str)
        assert cond == "(a = 1 or b = 2 or c = 3)"

    def test_with_expression(self) -> None:
        cond = or_("a = 1", and_("b = 2", "c = 3"))
        assert isinstance(cond, str)
        assert cond == "(a = 1 or (b = 2 and c = 3))"


class TestIn:

    def test_in_multiple_values(self) -> None:
        cond = in_("column1", ["1", "2", "3"])
        assert isinstance(cond, str)
        assert cond == "column1 in (1, 2, 3)"

    def test_in_single_value(self) -> None:
        cond = in_("column1", ["1"])
        assert isinstance(cond, str)
        assert cond == "column1 in (1)"
