from collections.abc import Iterable

from quack.storage.db import connect


def register_users(group_id: int, user_tags: Iterable[str]) -> list[str]:
    with connect() as connection:
        connection.executemany(
            """
            INSERT INTO
                group_registrations (group_id, user_id)
            VALUES
                (?, (SELECT user_id FROM users WHERE user_tag = ?));
            """,
            [(group_id, tag) for tag in user_tags],
        )

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
