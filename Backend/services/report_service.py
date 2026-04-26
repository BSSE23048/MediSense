"""
Report Service - Persistence and retrieval for user reports
"""

import json
from typing import Any, Dict, List, Optional

from services.storage_service import StorageService


class ReportService:
    def __init__(self):
        self.storage = StorageService()

    def save_report(
        self,
        user_id: int,
        report_title: str,
        extracted_text: str,
        summary: Dict[str, Any],
        medicines: Optional[List[Dict[str, Any]]] = None,
    ) -> int:
        return self.storage.execute(
            """
            INSERT INTO reports (user_id, report_title, extracted_text, summary_json, medicines_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                report_title,
                extracted_text,
                json.dumps(summary),
                json.dumps(medicines or []),
                self.storage.now(),
            ),
        )

    def list_reports(self, user_id: int) -> List[Dict[str, Any]]:
        rows = self.storage.fetch_all(
            "SELECT id, report_title, created_at FROM reports WHERE user_id = ? ORDER BY id DESC",
            (user_id,),
        )
        return rows

    def get_report(self, user_id: int, report_id: int) -> Optional[Dict[str, Any]]:
        row = self.storage.fetch_one(
            "SELECT * FROM reports WHERE id = ? AND user_id = ?",
            (report_id, user_id),
        )
        if not row:
            return None
        row["summary"] = json.loads(row["summary_json"])
        row["medicines"] = json.loads(row["medicines_json"] or "[]")
        return row

    def get_recent_report_context(self, user_id: int, limit: int = 3) -> str:
        rows = self.storage.fetch_all(
            "SELECT report_title, extracted_text FROM reports WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        )
        if not rows:
            return ""
        parts = []
        for row in rows:
            text = (row["extracted_text"] or "")[:1000]
            parts.append(f"Report: {row['report_title']}\n{text}")
        return "\n\n".join(parts)
