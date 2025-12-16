import importlib.util
import unittest

from hayagriva.config import ChunkingConfig
from hayagriva.core.chunker import WordChunker
from hayagriva.core.pipeline import build_prompt


class TestChunker(unittest.TestCase):
    def test_chunker_respects_window(self):
        config = ChunkingConfig(chunk_size=3, overlap=1)
        chunker = WordChunker(config)
        chunks = chunker.chunk(["one two three four five six"])
        self.assertEqual(chunks, ["one two three", "three four five", "five six"])


class TestPipeline(unittest.TestCase):
    def test_build_prompt_contains_question(self):
        prompt = build_prompt("What is RAG?", ["Retrieval augmented generation."])
        self.assertIn("Question: What is RAG?", prompt)


if __name__ == "__main__":
    unittest.main()