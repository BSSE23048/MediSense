import importlib.util
import sqlite3
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "storage_service", Path(__file__).parent / "services" / "storage_service.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class StorageBootstrapTests(unittest.TestCase):
    def test_fresh_database_creates_empty_runtime_tables(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "nested" / "app_data.db"
            module.StorageService(str(path))
            with sqlite3.connect(path) as db:
                for table in ("users", "reports", "chat_threads", "chat_messages"):
                    self.assertEqual(db.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0], 0)

    def test_reinitializing_preserves_existing_synthetic_records(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "app_data.db"
            storage = module.StorageService(str(path))
            storage.execute(
                "INSERT INTO users(email, password_hash, created_at) VALUES (?, ?, ?)",
                ("synthetic@example.test", "not-a-real-password-hash", "2026-01-01"),
            )
            reopened = module.StorageService(str(path))
            self.assertEqual(reopened.fetch_one("SELECT COUNT(*) AS count FROM users")["count"], 1)


if __name__ == "__main__":
    unittest.main()
