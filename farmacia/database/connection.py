import sqlite3
from pathlib import Path
from typing import Optional

DEFAULT_DB_DIR = Path(__file__).resolve().parent.parent / "data"
DEFAULT_DB_PATH = DEFAULT_DB_DIR / "farmacia.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection(db_path: Optional[str | Path] = None) -> sqlite3.Connection:
    if db_path is None:
        DEFAULT_DB_DIR.mkdir(parents=True, exist_ok=True)
        path = str(DEFAULT_DB_PATH)
    elif str(db_path) == ":memory:":
        path = ":memory:"
    else:
        path_obj = Path(db_path)
        if path_obj.parent and not path_obj.parent.exists():
            path_obj.parent.mkdir(parents=True, exist_ok=True)
        path = str(path_obj)

    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn: Optional[sqlite3.Connection] = None, db_path: Optional[str | Path] = None) -> sqlite3.Connection:
    if conn is None:
        conn = get_connection(db_path)

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        schema_sql = f.read()

    with conn:
        conn.executescript(schema_sql)

    return conn

