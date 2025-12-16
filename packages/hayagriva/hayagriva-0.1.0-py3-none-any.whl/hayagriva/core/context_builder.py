"""Context assembly utilities."""
from __future__ import annotations

from typing import Iterable, List


def build_context(chunks: Iterable[str]) -> str:
    """Concatenate retrieved chunks into a single context string."""

    return "\n\n".join(chunks)
