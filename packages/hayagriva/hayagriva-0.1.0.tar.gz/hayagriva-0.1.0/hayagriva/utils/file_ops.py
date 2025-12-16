"""File utilities for reading and writing text documents."""
from pathlib import Path
from typing import Iterable, List

from hayagriva.exceptions import IngestionError


def read_text_files(paths: Iterable[str]) -> List[str]:
    """Read text content from paths."""

    contents: List[str] = []
    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            raise IngestionError(f"Path does not exist: {path}")
        if path.is_dir():
            for child in path.glob("**/*.txt"):
                contents.append(child.read_text(encoding="utf-8"))
        else:
            contents.append(path.read_text(encoding="utf-8"))
    return contents
