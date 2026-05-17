import unittest
from pathlib import Path
from unittest.mock import patch

from rag.status import build_status_report
from rag.storage import RagStore


class StatusTests(unittest.TestCase):
    def test_status_report_includes_index_and_ollama_details(self):
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "rag.sqlite3"
            store = RagStore(db_path)
            try:
                store.add_chunk("data/example.md", 1, "Documents stay local.", [0.1, 0.2])
                store.commit()
                with patch("rag.status.fetch_ollama_models", return_value=["llama3.2:3b"]):
                    report = build_status_report(store, db_path)
            finally:
                store.close()

        self.assertIn("documents: 1", report)
        self.assertIn("chunks: 1", report)
        self.assertIn("server: available", report)
        self.assertIn("configured model installed: yes", report)


if __name__ == "__main__":
    unittest.main()
