"""Metadata structures for documents."""
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class DocumentMetadata:
    source: Optional[str] = None
    attributes: Dict[str, str] = field(default_factory=dict)
