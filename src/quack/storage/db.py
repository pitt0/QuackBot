import sqlite3
from pathlib import Path

DB_PATH = Path("data/quack.db")
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = connect()
    with open(SCHEMA_PATH) as f:
        conn.executescript(f.read())
    conn.commit()
