"""Parsing utilities for ingested documents."""
from __future__ import annotations

from typing import Iterable, List, Tuple


def to_records(documents: Iterable[str]) -> List[Tuple[str, dict]]:
    """Convert documents into (text, metadata) records."""

    return [(doc, {}) for doc in documents]
