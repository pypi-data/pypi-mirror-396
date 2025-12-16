"""Vector store implementations."""
from __future__ import annotations

import importlib.util
from typing import List, Sequence, Tuple

from hayagriva.exceptions import MissingDependencyError
from hayagriva.utils.logger import get_logger

logger = get_logger(__name__)


class FaissVectorStore:
    """A lightweight FAISS wrapper using inner-product search."""

    def __init__(self) -> None:
        if importlib.util.find_spec("faiss") is None:
            raise MissingDependencyError(
                "faiss-cpu is required for the FAISS vector store. Install with `pip install faiss-cpu`."
            )
        import faiss  # type: ignore

        self.faiss = faiss
        self.index: faiss.IndexFlatIP | None = None
        self.vectors: List[np.ndarray] = []
        self.chunks: List[str] = []

    def add(self, embeddings, chunks: Sequence[str]) -> None:
        if len(embeddings) != len(chunks):
            raise ValueError("Embeddings and chunks length mismatch")
        if embeddings.size == 0:
            return
        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = self.faiss.IndexFlatIP(dimension)
            logger.info("Initialized FAISS index with dimension %d", dimension)
        normalized = self._normalize(embeddings)
        self.index.add(normalized)
        self.vectors.extend(normalized)
        self.chunks.extend(list(chunks))

    def search(self, query_embedding, top_k: int = 4) -> List[Tuple[str, float]]:
        if self.index is None or len(self.chunks) == 0:
            return []
        normalized = self._normalize(query_embedding.reshape(1, -1))
        scores, indices = self.index.search(normalized, top_k)
        results: List[Tuple[str, float]] = []
        for score_row, idx_row in zip(scores, indices):
            for score, idx in zip(score_row, idx_row):
                if idx == -1:
                    continue
                results.append((self.chunks[idx], float(score)))
        return results

    def _normalize(self, vectors):
        if importlib.util.find_spec("numpy") is None:
            raise MissingDependencyError("numpy is required for vector operations.")
        import numpy as np

        norms = np.linalg.norm(vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        return vectors / norms
