"""Pipeline definitions for RAG workflows."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from hayagriva.core.context_builder import build_context


@dataclass
class RetrievalResult:
    context: str
    sources: List[str]


def build_prompt(question: str, contexts: Iterable[str]) -> str:
    """Compose a simple prompt from question and contexts."""

    context_block = build_context(contexts)
    return (
        "You are a helpful assistant. Use the provided context to answer the question.\n\n"
        f"Context:\n{context_block}\n\nQuestion: {question}\nAnswer:"
    )
