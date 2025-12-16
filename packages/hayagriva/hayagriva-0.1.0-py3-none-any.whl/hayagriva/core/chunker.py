"""Simple text chunker implementations."""
from __future__ import annotations

from typing import Iterable, List

from hayagriva.config import ChunkingConfig


class WordChunker:
    """Chunk text using a whitespace-based window."""

    def __init__(self, config: ChunkingConfig | None = None) -> None:
        self.config = config or ChunkingConfig()

    def chunk(self, documents: Iterable[str]) -> List[str]:
        chunks: List[str] = []
        for doc in documents:
            words = doc.split()
            size = self.config.chunk_size
            overlap = self.config.overlap
            start = 0
            while start < len(words):
                end = start + size
                chunk_words = words[start:end]
                if chunk_words:
                    chunks.append(" ".join(chunk_words))
                start += size - overlap if size > overlap else size
        return chunks
