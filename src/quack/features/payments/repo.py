from quack.storage.db import connect


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
