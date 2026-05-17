import unittest

from rag.embedding import cosine_similarity, embed


class EmbeddingTests(unittest.TestCase):
    def test_embedding_is_normalized_for_text(self):
        vector = embed("rag local documente personale")

        self.assertLess(abs(cosine_similarity(vector, vector) - 1.0), 0.000001)

    def test_embedding_for_empty_text_is_zero_vector(self):
        vector = embed("")

        self.assertEqual(vector, [0.0] * 256)


if __name__ == "__main__":
    unittest.main()
