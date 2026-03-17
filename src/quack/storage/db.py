import sqlite3
from pathlib import Path

DB_PATH = Path("data/quack.db")

BASE = Path(__file__).parent
SCHEMA_PATH = BASE / "schema.sql"
MIGRATIONS_DIR = BASE / "migrations"


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect()
    conn.executescript(SCHEMA_PATH.read_text())

    for file in MIGRATIONS_DIR.glob("*.sql"):
        version_id = file.name[:3]
        (is_present,) = conn.execute(
            """
            SELECT EXISTS (
                SELECT
                    1
                FROM
                    schema_migrations
                WHERE
                    version_id = ?
                );
            """,
            (int(version_id),),
        ).fetchone()

        if is_present:
            continue

        conn.executescript(file.read_text())

    conn.commit()
