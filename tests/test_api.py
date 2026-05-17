import unittest
from pathlib import Path

from rag.api import build_ask_response
from rag.storage import RagStore


class ApiTests(unittest.TestCase):
    def test_build_ask_response_includes_debug_and_sources(self):
        import tempfile

        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            store = RagStore(root / "rag.sqlite3")
            try:
                store.add_chunk(
                    "data/example.md",
                    1,
                    "The assistant can index notes and answer with cited sources.",
                    [0.1, 0.2],
                )
                store.commit()
                response = build_ask_response(store, "notes cited sources", llm=None, top_k=3)
            finally:
                store.close()

        self.assertEqual(response["question"], "notes cited sources")
        self.assertIn("answer", response)
        self.assertEqual(response["debug"]["retrieved_chunks"], 1)
        self.assertEqual(response["sources"][0]["path"], "data/example.md")


if __name__ == "__main__":
    unittest.main()
