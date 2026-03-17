CREATE TABLE IF NOT EXISTS group_registrations (
    id INTEGER PRIMARY KEY,

    group_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL
        REFERENCES users (user_id)
);
