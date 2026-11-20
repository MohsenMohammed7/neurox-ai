import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from app import main


class NeuroXApiTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self.temp_dir.name) / "test.db")
        self.db_patch = patch.object(main, "DB_PATH", self.db_path)
        self.db_patch.start()
        self.client = TestClient(main.app)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.db_patch.stop()
        self.temp_dir.cleanup()

    def test_health_reports_database(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["database"], "ok")

    def test_chat_creates_and_persists_conversation(self):
        with patch.dict("os.environ", {"AI_API_KEY": ""}, clear=False):
            response = self.client.post("/api/chat", json={"message": "مرحباً"})
        self.assertEqual(response.status_code, 200)
        conversation_id = response.json()["conversation_id"]

        listing = self.client.get("/api/conversations")
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(listing.json()["conversations"][0]["id"], conversation_id)

        detail = self.client.get(f"/api/conversations/{conversation_id}")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual([m["role"] for m in detail.json()["messages"]], ["user", "assistant"])

    def test_chat_reuses_conversation_id(self):
        first = self.client.post("/api/chat", json={"message": "الأول"})
        conversation_id = first.json()["conversation_id"]
        second = self.client.post(
            "/api/chat",
            json={"message": "الثاني", "conversation_id": conversation_id},
        )
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json()["conversation_id"], conversation_id)
        detail = self.client.get(f"/api/conversations/{conversation_id}")
        self.assertEqual(len(detail.json()["messages"]), 4)

    def test_delete_conversation(self):
        created = self.client.post("/api/chat", json={"message": "احذفني"})
        conversation_id = created.json()["conversation_id"]
        deleted = self.client.delete(f"/api/conversations/{conversation_id}")
        self.assertEqual(deleted.status_code, 200)
        self.assertEqual(self.client.get(f"/api/conversations/{conversation_id}").status_code, 404)


if __name__ == "__main__":
    unittest.main()
