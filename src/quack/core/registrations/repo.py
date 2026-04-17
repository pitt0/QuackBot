from quack.storage.db import connect


def check_registrations(group_id: int) -> list[str]:
    with connect() as connection:
        registrations = connection.execute(
            """
            SELECT
                COALESCE(usr.user_alias, usr.user_tag)
            FROM
                group_registrations AS reg
                INNER JOIN users AS usr
                ON reg.user_id = usr.user_id
            WHERE
                reg.group_id = ?;
            """,
            (group_id,),
        ).fetchall()

    return [r[0] for r in registrations]
