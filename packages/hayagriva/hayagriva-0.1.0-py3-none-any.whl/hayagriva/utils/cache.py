"""Lightweight in-memory cache utilities."""
from __future__ import annotations

import time
from typing import Any, Dict, Optional, Tuple


class MemoryCache:
    """A minimal TTL cache for reusing intermediate results."""

    def __init__(self) -> None:
        self._store: Dict[str, Tuple[Any, Optional[float]]] = {}

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        expires_at = time.time() + ttl if ttl else None
        self._store[key] = (value, expires_at)

    def get(self, key: str) -> Optional[Any]:
        value = self._store.get(key)
        if not value:
            return None
        payload, expires_at = value
        if expires_at and expires_at < time.time():
            del self._store[key]
            return None
        return payload

    def clear(self) -> None:
        self._store.clear()
