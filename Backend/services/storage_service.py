"""
Storage Service - SQLite persistence for users, reports, and chats
"""

import os
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional


class StorageService:
    """Simple SQLite-backed storage used by API routes and services."""

    def __init__(self, db_path: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.db_path = db_path or os.path.join(base_dir, "database", "app_data.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _connect(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    report_title TEXT NOT NULL,
                    extracted_text TEXT NOT NULL,
                    summary_json TEXT NOT NULL,
                    medicines_json TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                );

                CREATE TABLE IF NOT EXISTS chat_threads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    report_id INTEGER,
                    title TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES users(id),
                    FOREIGN KEY(report_id) REFERENCES reports(id)
                );

                CREATE TABLE IF NOT EXISTS chat_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id INTEGER NOT NULL,
                    role TEXT NOT NULL,
                    message TEXT NOT NULL,
                    sources_json TEXT DEFAULT '[]',
                    created_at TEXT NOT NULL,
                    FOREIGN KEY(thread_id) REFERENCES chat_threads(id)
                );
                """
            )

    def now(self) -> str:
        return datetime.utcnow().isoformat()

    def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute(query, params).fetchone()
            return dict(row) if row else None

    def fetch_all(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]

    def execute(self, query: str, params: tuple = ()) -> int:
        with self._connect() as conn:
            cur = conn.execute(query, params)
            conn.commit()
            return cur.lastrowid
