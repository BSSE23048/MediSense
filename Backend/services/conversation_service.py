"""
Conversation Service - Chat thread and message persistence
"""

import json
from typing import Any, Dict, List

from services.storage_service import StorageService


class ConversationService:
    def __init__(self):
        self.storage = StorageService()

    def create_or_resume_thread(self, user_id: int, report_id: int = None, title: str = "Report Follow-up") -> Dict[str, Any]:
        if report_id:
            existing = self.storage.fetch_one(
                "SELECT * FROM chat_threads WHERE user_id = ? AND report_id = ? ORDER BY id DESC LIMIT 1",
                (user_id, report_id),
            )
            if existing:
                return existing

        thread_id = self.storage.execute(
            """
            INSERT INTO chat_threads (user_id, report_id, title, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (user_id, report_id, title, self.storage.now(), self.storage.now()),
        )
        return self.storage.fetch_one("SELECT * FROM chat_threads WHERE id = ?", (thread_id,))

    def list_messages(self, user_id: int, thread_id: int) -> List[Dict[str, Any]]:
        thread = self.storage.fetch_one(
            "SELECT id FROM chat_threads WHERE id = ? AND user_id = ?",
            (thread_id, user_id),
        )
        if not thread:
            return []
        rows = self.storage.fetch_all(
            "SELECT role, message, sources_json, created_at FROM chat_messages WHERE thread_id = ? ORDER BY id ASC",
            (thread_id,),
        )
        for row in rows:
            row["sources"] = json.loads(row["sources_json"] or "[]")
        return rows

    def add_message(self, thread_id: int, role: str, message: str, sources: List[str] = None):
        self.storage.execute(
            """
            INSERT INTO chat_messages (thread_id, role, message, sources_json, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (thread_id, role, message, json.dumps(sources or []), self.storage.now()),
        )
        self.storage.execute(
            "UPDATE chat_threads SET updated_at = ? WHERE id = ?",
            (self.storage.now(), thread_id),
        )

    def get_recent_memory(self, user_id: int, thread_id: int, max_turns: int = 8) -> str:
        messages = self.list_messages(user_id, thread_id)
        if not messages:
            return ""
        messages = messages[-max_turns:]
        lines = []
        for msg in messages:
            prefix = "User" if msg["role"] == "user" else "Assistant"
            lines.append(f"{prefix}: {msg['message']}")
        return "\n".join(lines)
