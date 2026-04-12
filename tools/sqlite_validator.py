"""
SQLite DDL validation tool.
Executes DDL statements in an in-memory database to verify correctness.
"""

import sqlite3


def validate_ddl(ddl_code: str) -> tuple[bool, str]:
    """
    Attempt to execute *ddl_code* inside an in-memory SQLite database.

    Returns
    -------
    (True,  "SUCCESS")           — if all statements executed without error.
    (False, "<error message>")   — on any failure.
    """
    conn = None
    try:
        conn = sqlite3.connect(":memory:")
        conn.execute("PRAGMA foreign_keys = ON;")
        conn.executescript(ddl_code)
        conn.commit()
        return True, "SUCCESS"
    except Exception as e:
        return False, str(e)
    finally:
        if conn:
            conn.close()
