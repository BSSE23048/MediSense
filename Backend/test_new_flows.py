import os
import unittest
import sys

os.environ["SECRET_KEY"] = "test-secret"
sys.path.insert(0, os.path.dirname(__file__))

from app import app  # noqa: E402


class NewFlowsTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.email = "qa_user@example.com"
        self.password = "test1234"
        self.token = self._register_or_login()

    def _register_or_login(self):
        register = self.client.post(
            "/api/auth/register",
            json={"email": self.email, "password": self.password},
        )
        if register.status_code in (200, 201):
            return register.get_json()["token"]
        login = self.client.post(
            "/api/auth/login",
            json={"email": self.email, "password": self.password},
        )
        return login.get_json()["token"]

    def test_report_save_and_retrieve(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        summarize = self.client.post(
            "/api/summarize",
            json={"text": "Patient has fever and was prescribed Panadol.", "report_title": "Test Report"},
            headers=headers,
        )
        self.assertEqual(summarize.status_code, 200)
        payload = summarize.get_json()
        self.assertTrue(payload["success"])
        self.assertIn("saved_report_id", payload)

        reports = self.client.get("/api/reports", headers=headers)
        self.assertEqual(reports.status_code, 200)
        self.assertTrue(reports.get_json()["reports"])

    def test_chat_followup_flow(self):
        headers = {"Authorization": f"Bearer {self.token}"}
        thread = self.client.post("/api/chat/thread", json={}, headers=headers)
        self.assertEqual(thread.status_code, 200)
        thread_id = thread.get_json()["thread"]["id"]

        ask = self.client.post(
            f"/api/chat/thread/{thread_id}/ask",
            json={"question": "Can I ask follow-up on my report?"},
            headers=headers,
        )
        self.assertEqual(ask.status_code, 200)
        self.assertTrue(ask.get_json()["success"])


if __name__ == "__main__":
    unittest.main()
