"""Token and text utilities."""
from typing import Iterable, List


def count_words(text: str) -> int:
    """Count words in a string using whitespace tokenization."""

    return len(text.split())


def batch_words(texts: Iterable[str]) -> List[int]:
    """Return word counts for a collection of strings."""

    return [count_words(text) for text in texts]
