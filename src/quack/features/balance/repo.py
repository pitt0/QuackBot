from quack.storage.db import connect


def fetch_balance(group_id: int) -> list[tuple[str, int]]:
    with connect() as connection:
        query = """
        WITH group_members AS (
            SELECT
                usr.user_id,
                COALESCE(user_alias, user_tag) AS user_handle
            FROM users AS usr
            INNER JOIN group_registrations AS gr
                ON usr.user_id = gr.user_id
            WHERE gr.group_id = ?
        ),

        debts AS (
            SELECT
                gmp.user_handle AS creditor,
                gme.user_handle AS debtor,
                exp.amount
            FROM purchase_record AS pr
            INNER JOIN group_members AS gmp
                ON gmp.user_id = pr.creator_id
            INNER JOIN expenses AS exp
                ON exp.purchase_id = pr.purchase_id
            INNER JOIN group_members AS gme
                ON gme.user_id = exp.user_id
            WHERE exp.user_id != pr.creator_id
        )

        SELECT
            user,
            SUM(balance) AS net_balance
        FROM (
            SELECT creditor AS user, amount AS balance FROM debts
            UNION ALL
            SELECT debtor   AS user, -amount AS balance FROM debts
        )
        GROUP BY user
        ORDER BY net_balance DESC;
        """
        return connection.execute(query, (group_id,)).fetchall()
