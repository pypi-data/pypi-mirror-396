import unittest

from hayagriva.ingestion.loaders import load_texts
from hayagriva.utils.validator import ensure_texts


class TestIngestion(unittest.TestCase):
    def test_load_texts_filters_empty(self):
        docs = ["hello", " ", "world"]
        loaded = load_texts(docs)
        self.assertEqual(loaded, ["hello", "world"])

    def test_ensure_texts_raises_on_empty(self):
        with self.assertRaises(Exception):
            ensure_texts(["   ", ""])


if __name__ == "__main__":
    unittest.main()
