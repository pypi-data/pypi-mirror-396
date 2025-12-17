from buildsql import select, select_distinct


class TestSelect:

    # TODO: combinations of statements

    def test_select_only(self) -> None:
        sql = select("1").build()
        assert sql == "select 1"

    def test_select_from(self) -> None:
        sql = select("1").from_("table1").build()
        assert sql == "select 1\nfrom table1"

    def test_select_where(self) -> None:
        sql = select("1").from_("table1").where("id = 10").build()
        assert sql == "select 1\nfrom table1\nwhere id = 10"

    def test_select_group_by(self) -> None:
        sql = select("1").from_("table1").group_by("col1").build()
        assert sql == "select 1\nfrom table1\ngroup by col1"

    def test_select_having(self) -> None:
        sql = (
            select("1")
            .from_("table1")
            .group_by("col1")
            .having("count(col1) > 1")
            .build()
        )
        assert sql == "select 1\nfrom table1\ngroup by col1\nhaving count(col1) > 1"

    def test_select_order_by(self) -> None:
        sql = select("1").from_("table1").order_by("col1", ("col2", "desc")).build()
        assert sql == "select 1\nfrom table1\norder by col1, col2 desc"

    def test_select_limit(self) -> None:
        sql = select("1").from_("table1").limit(10).build()
        assert sql == "select 1\nfrom table1\nlimit 10"

    def test_select_offset(self) -> None:
        sql = select("1").from_("table1").offset(5).build()
        assert sql == "select 1\nfrom table1\noffset 5 rows"

    def test_select_fetch(self) -> None:
        sql = select("1").from_("table1").fetch("first", 10, "only").build()
        assert sql == "select 1\nfrom table1\nfetch first 10 rows only"

    def test_select_inner_join(self) -> None:
        sql = (
            select("1")
            .from_("table1")
            .inner_join("table2", on="table1.id = table2.t1_id")
            .build()
        )
        assert (
            sql
            == "select 1\nfrom table1\ninner join table2 on table1.id = table2.t1_id"
        )

    def test_select_left_join(self) -> None:
        sql = (
            select("1")
            .from_("table1")
            .left_join("table2", on="table1.id = table2.t1_id")
            .build()
        )
        assert (
            sql == "select 1\nfrom table1\nleft join table2 on table1.id = table2.t1_id"
        )

    def test_select_right_join(self) -> None:
        sql = (
            select("1")
            .from_("table1")
            .right_join("table2", on="table1.id = table2.t1_id")
            .build()
        )
        assert (
            sql
            == "select 1\nfrom table1\nright join table2 on table1.id = table2.t1_id"
        )

    def test_select_full_join(self) -> None:
        sql = (
            select("1")
            .from_("table1")
            .full_join("table2", on="table1.id = table2.t1_id")
            .build()
        )
        assert (
            sql == "select 1\nfrom table1\nfull join table2 on table1.id = table2.t1_id"
        )

    def test_select_cross_join(self) -> None:
        sql = select("1").from_("table1").cross_join("table2").build()
        assert sql == "select 1\nfrom table1\ncross join table2"

    def test_select_lateral_join(self) -> None:
        sql = (
            select("1")
            .from_("table1")
            .lateral_join("table2", on="table1.id = table2.t1_id")
            .build()
        )
        assert (
            sql
            == "select 1\nfrom table1\nlateral join table2 on table1.id = table2.t1_id"
        )


class TestSelectDistinct:

    # TODO: add more here...

    def test_select_distinct_only(self) -> None:
        sql = select_distinct("1").build()
        assert sql == "select distinct 1"

    def test_select_distinct_from(self) -> None:
        sql = select_distinct("1").from_("table1").build()
        assert sql == "select distinct 1\nfrom table1"

    def test_select_distinct_on_from(self) -> None:
        sql = select_distinct("col1").on("col2").from_("table1").build()
        assert sql == "select distinct on (col2) col1\nfrom table1"
