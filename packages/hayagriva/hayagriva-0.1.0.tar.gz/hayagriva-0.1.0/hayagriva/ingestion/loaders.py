"""Document loader utilities."""
from __future__ import annotations

from typing import Iterable, List

from hayagriva.exceptions import IngestionError
from hayagriva.utils.file_ops import read_text_files
from hayagriva.utils.validator import ensure_texts


def load_texts(docs: Iterable[str]) -> List[str]:
    """Load raw text from an iterable of strings."""

    return ensure_texts(docs)


def load_from_paths(paths: Iterable[str]) -> List[str]:
    """Load text contents from filesystem paths."""

    try:
        return read_text_files(paths)
    except OSError as exc:  # pylint: disable=broad-except
        raise IngestionError(f"Failed to read paths: {exc}") from exc
