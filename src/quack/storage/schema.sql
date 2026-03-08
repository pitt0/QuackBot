PRAGMA foreign_keys = ON;


CREATE TABLE IF NOT EXISTS schema_migrations (
    version_id INTEGER UNIQUE NOT NULL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    user_tag TEXT UNIQUE NOT NULL,
    user_alias TEXT
);


CREATE TABLE IF NOT EXISTS purchase_record (
    purchase_id INTEGER PRIMARY KEY,
    creator_id INTEGER NOT NULL,

    purchase_label TEXT DEFAULT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (creator_id) REFERENCES users (user_id)
);


CREATE TABLE IF NOT EXISTS expenses (
    purchase_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,

    amount INTEGER NOT NULL DEFAULT 0, -- NOTE: stored in cents

    PRIMARY KEY (purchase_id, user_id),
    FOREIGN KEY (purchase_id) REFERENCES purchase_record (purchase_id),
    FOREIGN KEY (user_id) REFERENCES users (user_id)
);
