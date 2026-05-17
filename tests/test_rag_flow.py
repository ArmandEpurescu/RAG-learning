import unittest
from pathlib import Path

from rag.answering import answer_from_results
from rag.ingest import ingest_path
from rag.retrieval import search
from rag.storage import RagStore


class RagFlowTests(unittest.TestCase):
    def test_ingest_search_and_answer(self):
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            data_dir = root / "data"
            data_dir.mkdir()
            note = data_dir / "note.md"
            note.write_text(
                "Proiectul RAG pastreaza documentele local si foloseste surse citate.",
                encoding="utf-8",
            )

            store = RagStore(root / "rag.sqlite3")
            try:
                count = ingest_path(store, data_dir, reset=True)
                results = search(store, "documente local surse", top_k=3)
                answer = answer_from_results("Cum sunt pastrate documentele?", results)
            finally:
                store.close()

            self.assertEqual(count, 1)
            self.assertTrue(results)
            self.assertIn("documentele local", answer)
            self.assertIn("note.md#1", answer)


if __name__ == "__main__":
    unittest.main()
