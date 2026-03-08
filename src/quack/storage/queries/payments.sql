-- name: create_purchase_record
INSERT INTO
    purchase_record (creator_id, purchase_label)
VALUES
    ((SELECT user_id FROM users WHERE user_tag = ?), ?)
RETURNING
    purchase_id;


-- name: add_expense
INSERT INTO
    expenses (purchase_id, user_id, amount)
VALUES
    (?, (SELECT user_id FROM users WHERE user_tag = ?), ?);


-- name: get_history
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
    ON pr.creator_id = u.user_id;
