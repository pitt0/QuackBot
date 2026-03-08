INSERT OR IGNORE INTO
    users (user_tag)
VALUES
    (?)
RETURNING
    user_id;
