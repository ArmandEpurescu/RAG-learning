import os
import unittest
from unittest.mock import patch

from rag.llm import build_rag_prompt, load_ollama_config
from rag.retrieval import SearchResult
from rag.storage import StoredChunk


class LlmTests(unittest.TestCase):
    def test_build_rag_prompt_includes_question_and_sources(self):
        result = SearchResult(
            chunk=StoredChunk(
                id=1,
                path="data/rag-learning.md",
                chunk_index=1,
                text="Documents stay local.",
                embedding=[],
            ),
            score=0.42,
        )

        prompt = build_rag_prompt("Where are documents stored?", [result])

        self.assertIn("Where are documents stored?", prompt)
        self.assertIn("data/rag-learning.md#1", prompt)
        self.assertIn("Documents stay local.", prompt)

    def test_ollama_config_defaults_to_small_local_model(self):
        with patch.dict(os.environ, {}, clear=True):
            config = load_ollama_config()

        self.assertEqual(config.model, "llama3.2:3b")
        self.assertEqual(config.base_url, "http://localhost:11434")


if __name__ == "__main__":
    unittest.main()
