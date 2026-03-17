from .db import connect


def persist_purchase(creator: str, debts: dict[str, int], purchase_label: str | None) -> None:
    with connect() as connection:
        (purchase_id,) = connection.execute(
            """
            INSERT INTO
                purchase_record (creator_id, purchase_label)
            VALUES
                ((
                    SELECT
                        user_id
                    FROM
                        users
                    WHERE
                        user_tag = :req OR
                        user_alias = :req
                ), :p_label)
            RETURNING
                purchase_id;
            """,
            {"req": creator, "p_label": purchase_label},
        ).fetchone()

        connection.executemany(
            """
            INSERT INTO
                expenses (purchase_id, user_id, amount)
            VALUES
                (:p_id, (
                    SELECT
                        user_id
                    FROM
                        users
                    WHERE
                        user_tag = :u_ref OR
                        user_alias = :u_ref
                ), :exp);
            """,
            [{"p_id": purchase_id, "u_ref": u, "exp": d} for u, d in debts.items()],
        )


def fetch_history() -> list[tuple[str, str | None, str, str, int]]:
    with connect() as connection:
        query = """
        SELECT
            COALESCE(pu.user_alias, pu.user_tag),
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
