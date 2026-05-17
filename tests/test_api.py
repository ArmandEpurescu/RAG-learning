import unittest
from http.client import HTTPConnection
from pathlib import Path
from threading import Thread

from rag.api import RagApiHandler, build_ask_response
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

    def test_invalid_json_returns_400(self):
        import tempfile
        from http.server import ThreadingHTTPServer

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "rag.sqlite3"
            handler = type("TestHandler", (RagApiHandler,), {"db_path": db_path})
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()

            try:
                connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request(
                    "POST",
                    "/ask",
                    body='{"question": "broken"',
                    headers={"Content-Type": "application/json"},
                )
                response = connection.getresponse()
                body = response.read().decode("utf-8")
                connection.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(response.status, 400)
        self.assertIn("Invalid JSON", body)

    def test_index_page_is_served(self):
        import tempfile
        from http.server import ThreadingHTTPServer

        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "rag.sqlite3"
            handler = type("TestHandler", (RagApiHandler,), {"db_path": db_path})
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = Thread(target=server.serve_forever, daemon=True)
            thread.start()

            try:
                connection = HTTPConnection("127.0.0.1", server.server_port, timeout=5)
                connection.request("GET", "/")
                response = connection.getresponse()
                body = response.read().decode("utf-8")
                connection.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=5)

        self.assertEqual(response.status, 200)
        self.assertIn("RAG Learning", body)


if __name__ == "__main__":
    unittest.main()
