# engines/memory/postgres_backend.py
# Repurposed as SQLite backend (lightweight local mode)

import json
import sqlite3
from datetime import datetime, timedelta
from orbmem.utils.logger import get_logger
from orbmem.utils.exceptions import DatabaseError

logger = get_logger(__name__)

DB_PATH = "ocdb.sqlite3"


class PostgresMemoryBackend:
    """
    Lightweight SQLite-based memory engine.
    Replaces PostgreSQL for systems with low storage.
    """

    def __init__(self):
        try:
            self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
            self.cursor = self.conn.cursor()
            self._init_tables()
            logger.info("SQLite Memory Backend initialized (replacing PostgreSQL).")
        except Exception as e:
            raise DatabaseError(f"SQLite init error: {e}")

    # ---------------------------------------------------------
    # Create tables if missing
    # ---------------------------------------------------------
    def _init_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory (
                key TEXT PRIMARY KEY,
                value TEXT,
                session_id TEXT,
                expires_at TEXT
            )
        """)
        self.conn.commit()

    # ---------------------------------------------------------
    # Set memory key
    # ---------------------------------------------------------
    def set(self, key: str, value, session_id: str = None, ttl_seconds: int = None):
        try:
            expires_at = None
            if ttl_seconds:
                expires_at = (datetime.utcnow() + timedelta(seconds=ttl_seconds)).isoformat()

            value_json = json.dumps(value)

            self.cursor.execute("""
                INSERT INTO memory (key, value, session_id, expires_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value=excluded.value,
                    session_id=excluded.session_id,
                    expires_at=excluded.expires_at
            """, (key, value_json, session_id, expires_at))

            self.conn.commit()

        except Exception as e:
            raise DatabaseError(f"SQLite write error: {e}")

    # ---------------------------------------------------------
    # Get memory key
    # ---------------------------------------------------------
    def get(self, key: str):
        try:
            self.cursor.execute("SELECT value, expires_at FROM memory WHERE key=?", (key,))
            row = self.cursor.fetchone()

            if not row:
                return None

            value_json, expires_at = row

            # TTL check
            if expires_at:
                if datetime.utcnow() > datetime.fromisoformat(expires_at):
                    self.delete(key)
                    return None

            return json.loads(value_json)

        except Exception as e:
            raise DatabaseError(f"SQLite read error: {e}")

    # ---------------------------------------------------------
    # Delete a memory key
    # ---------------------------------------------------------
    def delete(self, key: str):
        try:
            self.cursor.execute("DELETE FROM memory WHERE key=?", (key,))
            self.conn.commit()
        except Exception as e:
            raise DatabaseError(f"SQLite delete error: {e}")

    # ---------------------------------------------------------
    # List memory keys
    # ---------------------------------------------------------
    def keys(self):
        try:
            self.cursor.execute("SELECT key FROM memory")
            rows = self.cursor.fetchall()
            return [r[0] for r in rows]
        except Exception as e:
            raise DatabaseError(f"SQLite keys error: {e}")
