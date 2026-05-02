from quack.storage.db import connect


def fetch_history(group_id: int) -> list[tuple[str, str | None, str, str, int]]:
    with connect() as connection:
        query = """
        WITH group_members AS (
            SELECT
                user_id,
                COALESCE(user_alias, user_tag) AS user_handle,
                user_tag
            FROM
                users AS usr
                INNER JOIN group_registrations AS gr
                ON usr.user_id = gr.user_id
            WHERE
                gr.group_id = ?
        )

        SELECT
            gme.user_handle,
            pr.purchase_label,
            pr.created_at,
            gme.user_tag,
            exp.amount

        FROM
            purchase_record AS pr

            INNER JOIN group_members AS gmp
            ON gmp.user_id = pr.creator_id

            INNER JOIN expenses AS exp
            ON exp.purchase_id = pr.purchase_id

            INNER JOIN group_members AS gme
            ON exp.user_id = gme.user_id;
        """
        return connection.execute(query, (group_id,)).fetchall()
