from buildsql import delete_from


class TestDeleteFrom:

    def test_delete_from_only(self) -> None:
        sql = delete_from("users").build()
        assert sql == "delete from users"

    def test_delete_from_using_where(self) -> None:
        sql = (
            delete_from("users")
            .using("table1")
            .where("users.id = table1.user_id")
            .build()
        )
        assert sql == "delete from users\nusing table1\nwhere users.id = table1.user_id"

    def test_delete_from_using_where_returning(self) -> None:
        sql = (
            delete_from("users")
            .using("table1")
            .where("users.id = table1.user_id")
            .returning("id, name")
            .build()
        )
        assert (
            sql
            == "delete from users\nusing table1\nwhere users.id = table1.user_id\nreturning id, name"
        )

    def test_delete_from_where(self) -> None:
        sql = delete_from("users").where("id = 10").build()
        assert sql == "delete from users\nwhere id = 10"

    def test_delete_from_where_returning(self) -> None:
        sql = delete_from("users").where("id = 10").returning("id, name").build()
        assert sql == "delete from users\nwhere id = 10\nreturning id, name"

    def test_delete_from_returning(self) -> None:
        sql = delete_from("users").returning("id, name").build()
        assert sql == "delete from users\nreturning id, name"
