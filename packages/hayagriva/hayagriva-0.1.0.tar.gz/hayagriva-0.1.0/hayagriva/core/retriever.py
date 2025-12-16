"""Retriever implementations."""
from __future__ import annotations

from typing import Iterable, List, Tuple

from hayagriva.config import RetrievalConfig
from hayagriva.core.embeddings import SentenceTransformerEmbeddings
from hayagriva.core.vectorstore import FaissVectorStore
from hayagriva.utils.logger import get_logger
from hayagriva.utils.validator import validate_top_k

logger = get_logger(__name__)


class Retriever:
    """Combine embedding model and vector store for retrieval."""

    def __init__(
        self,
        embedder: SentenceTransformerEmbeddings,
        vector_store: FaissVectorStore,
        config: RetrievalConfig | None = None,
    ) -> None:
        self.embedder = embedder
        self.vector_store = vector_store
        self.config = config or RetrievalConfig()

    def add(self, chunks: Iterable[str]) -> None:
        chunk_list = list(chunks)
        embeddings = self.embedder.embed(chunk_list)
        self.vector_store.add(embeddings, chunk_list)
        logger.info("Added %d chunks to vector store", len(chunk_list))

    def retrieve(self, query: str) -> List[Tuple[str, float]]:
        top_k = validate_top_k(self.config.top_k)
        query_embedding = self.embedder.embed_query(query)
        results = self.vector_store.search(query_embedding, top_k=top_k)
        if self.config.similarity_threshold > 0:
            results = [r for r in results if r[1] >= self.config.similarity_threshold]
        logger.info("Retrieved %d chunks", len(results))
        return results
