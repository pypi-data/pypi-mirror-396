from buildsql import update


class TestUpdate:

    def test_update_only(self) -> None:
        sql = update("users").set("name = 'John'").build()
        assert sql == "update users\nset name = 'John'"

    def test_update_from(self) -> None:
        sql = update("users").set("name = 'John'").from_("table1").build()
        assert sql == "update users\nset name = 'John'\nfrom table1"

    def test_update_from_returning(self) -> None:
        sql = (
            update("users")
            .set("name = 'John'")
            .from_("table1")
            .returning("id, name")
            .build()
        )
        assert sql == "update users\nset name = 'John'\nfrom table1\nreturning id, name"

    def test_update_where(self) -> None:
        sql = update("users").set("name = 'John'").where("id = 10").build()
        assert sql == "update users\nset name = 'John'\nwhere id = 10"

    def test_update_from_where(self) -> None:
        sql = (
            update("users")
            .set("name = 'John'")
            .from_("table1")
            .where("users.id = table1.user_id")
            .build()
        )
        assert (
            sql
            == "update users\nset name = 'John'\nfrom table1\nwhere users.id = table1.user_id"
        )

    def test_update_from_where_returning(self) -> None:
        sql = (
            update("users")
            .set("name = 'John'")
            .from_("table1")
            .where("users.id = table1.user_id")
            .returning("id, name")
            .build()
        )
        assert (
            sql
            == "update users\nset name = 'John'\nfrom table1\nwhere users.id = table1.user_id\nreturning id, name"
        )

    def test_update_where_returning(self) -> None:
        sql = (
            update("users")
            .set("name = 'John'")
            .where("id = 10")
            .returning("id, name")
            .build()
        )
        assert (
            sql == "update users\nset name = 'John'\nwhere id = 10\nreturning id, name"
        )

    def test_update_returning(self) -> None:
        sql = (
            update("users")
            .set("name = 'John'")
            .where("id = 10")
            .returning("id, name")
            .build()
        )
        assert (
            sql == "update users\nset name = 'John'\nwhere id = 10\nreturning id, name"
        )
