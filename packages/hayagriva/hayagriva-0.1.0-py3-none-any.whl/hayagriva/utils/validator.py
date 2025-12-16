"""Validation helpers for user inputs."""
from typing import Iterable, List

from hayagriva.exceptions import ConfigurationError, IngestionError


def ensure_texts(docs: Iterable[str]) -> List[str]:
    """Ensure the provided documents are a non-empty iterable of strings."""

    if docs is None:
        raise IngestionError("No documents provided for ingestion.")
    texts = [doc for doc in docs if isinstance(doc, str) and doc.strip()]
    if not texts:
        raise IngestionError("Documents must be non-empty strings.")
    return texts


def validate_top_k(top_k: int) -> int:
    if top_k <= 0:
        raise ConfigurationError("top_k must be greater than zero")
    return top_k
