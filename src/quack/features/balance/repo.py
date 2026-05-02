from quack.storage.db import connect


def fetch_history(group_id: int) -> list[tuple[str, str | None, str, str, int]]:
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
            ON pr.creator_id = pu.user_id
        WHERE
            group_id = ?;
        """
        return connection.execute(query, (group_id,)).fetchall()
