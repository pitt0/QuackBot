from .db import connect


def persist_purchase(creator: str, debts: dict[str, int], purchase_label: str | None) -> None:
    with connect() as connection:
        connection.executemany("INSERT OR IGNORE INTO users (user_tag) VALUES (?);", [(u,) for u in debts])
        (purchase_id,) = connection.execute(
            "INSERT INTO purchase_record (creator_id, purchase_label) VALUES ((SELECT user_id FROM users WHERE user_tag = ?), ?) RETURNING purchase_id;",
            (creator, purchase_label),
        ).fetchone()

        connection.executemany(
            "INSERT INTO expenses (purchase_id, user_id, amount) VALUES (?, (SELECT user_id FROM users WHERE user_tag = ?), ?);",
            [(purchase_id, u, d) for u, d in debts.items()],
        )


def fetch_history() -> list[tuple[str, str | None, str, str, int]]:
    with connect() as connection:
        query = """
        SELECT
            pu.user_tag,
            pr.purchase_label,
            pr.created_at,
            u.user_tag,
            e.amount

        FROM
            purchase_record AS pr

            INNER JOIN expenses AS e
            USING (purchase_id)

            INNER JOIN users AS u
            ON e.user_id = u.user_id

            INNER JOIN users AS pu
            ON pr.creator_id = pu.user_id;
        """
        return connection.execute(query).fetchall()
