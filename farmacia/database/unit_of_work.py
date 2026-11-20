import sqlite3
from interfaces.transaction import IUnitOfWork


class SqliteUnitOfWork(IUnitOfWork):
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()

    def rollback(self) -> None:
        self.conn.rollback()

