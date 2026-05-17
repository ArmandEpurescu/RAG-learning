import unittest

from rag.chunking import chunk_text


class ChunkingTests(unittest.TestCase):
    def test_chunk_text_keeps_short_text_as_one_chunk(self):
        chunks = chunk_text("Prima nota.\n\nA doua nota.", chunk_size=100)

        self.assertEqual(len(chunks), 1)
        self.assertIn("Prima nota", chunks[0].text)
        self.assertIn("A doua nota", chunks[0].text)

    def test_chunk_text_splits_long_text(self):
        text = " ".join(f"cuvant{i}." for i in range(120))

        chunks = chunk_text(text, chunk_size=120, overlap=20)

        self.assertGreater(len(chunks), 1)
        self.assertTrue(all(chunk.text for chunk in chunks))


if __name__ == "__main__":
    unittest.main()
