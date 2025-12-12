# backend/auth_database.py
# Compatibility wrapper so existing auth services (which use %s placeholders
# and expect a DB connection like pymysql) can work with SQLite.

import sqlite3
import os
from contextlib import contextmanager

DB_FILE = os.getenv("AUTH_DB_FILE", os.path.join(os.path.dirname(__file__), "auth.db"))

# Helper to convert MySQL-style %s placeholders to SQLite-friendly ? placeholders.
def _convert_query(query):
    return query.replace("%s", "?")

class _CursorWrapper:
    def __init__(self, cursor):
        self._cursor = cursor

    # Support context manager: "with conn.cursor() as cursor:"
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._cursor.close()
        except Exception:
            pass
        # Do not suppress exceptions
        return False

    def execute(self, query, params=None):
        q = _convert_query(query)
        if params is None:
            return self._cursor.execute(q)
        return self._cursor.execute(q, params)

    def executemany(self, query, seq_of_params):
        q = _convert_query(query)
        return self._cursor.executemany(q, seq_of_params)

    def fetchone(self):
        row = self._cursor.fetchone()
        # convert sqlite3.Row to dict-like for compatibility
        if isinstance(row, sqlite3.Row):
            return dict(row)
        return row

    def fetchall(self):
        rows = self._cursor.fetchall()
        return [dict(r) if isinstance(r, sqlite3.Row) else r for r in rows]

    def close(self):
        try:
            self._cursor.close()
        except Exception:
            pass

    @property
    def rowcount(self):
        return getattr(self._cursor, "rowcount", -1)

class _ConnectionWrapper:
    def __init__(self, conn):
        self._conn = conn

    # allow "with get_db_connection() as conn:" usage
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            self._conn.commit()
            self._conn.close()
        except Exception:
            pass
        return False

    def cursor(self):
        return _CursorWrapper(self._conn.cursor())

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        try:
            self._conn.close()
        except Exception:
            pass

@contextmanager
def get_db_connection():
    """Context manager that yields a connection wrapper (use like: with get_db_connection() as conn:)"""
    conn = sqlite3.connect(DB_FILE, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
    # let rows be accessible by column name
    conn.row_factory = sqlite3.Row
    # enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield _ConnectionWrapper(conn)
    finally:
        try:
            conn.commit()
        except Exception:
            pass
        try:
            conn.close()
        except Exception:
            pass
