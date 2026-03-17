from collections.abc import Iterable

from .db import connect


def persist_users(user_tags: list[str]) -> None:
    with connect() as connection:
        connection.executemany(
            """
            INSERT OR IGNORE INTO
                users (user_tag)
            VALUES
                (?);
            """,
            ((tag,) for tag in user_tags),
        )


def persist_alias(user_tag: str, user_alias: str) -> None:
    with connect() as connection:
        connection.execute(
            """
            INSERT OR REPLACE INTO
                users (user_tag, user_alias)
            VALUES
                (?, ?);
            """,
            (user_tag, user_alias),
        )


def check_alias_existence(user_alias: str) -> bool:
    with connect() as connection:
        (flag,) = connection.execute(
            """
            SELECT EXISTS (
                SELECT
                    1
                FROM
                    users
                WHERE
                    user_alias = ?;
                );
            """,
            (user_alias,),
        ).fetchone()

    return flag


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


def set_alias(user_tag: str, user_alias: str) -> None:
    with connect() as connection:
        connection.execute("INSERT OR REPLACE INTO users (user_tag, user_alias) VALUES (?, ?);", (user_tag, user_alias))


def get_user_by_alias(user_alias: str) -> str | None:
    with connect() as connection:
        res = connection.execute("SELECT user_tag FROM users WHERE user_alias = ?;", (user_alias,)).fetchone()
        return res[0] if res else None
