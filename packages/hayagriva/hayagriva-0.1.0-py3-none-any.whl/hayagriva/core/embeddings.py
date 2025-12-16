"""Embedding providers."""
from __future__ import annotations

import importlib.util
from typing import Iterable, Optional

from hayagriva.exceptions import MissingDependencyError
from hayagriva.utils.logger import get_logger

logger = get_logger(__name__)


class SentenceTransformerEmbeddings:
    """Sentence-Transformers embedding wrapper."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: Optional[str] = None) -> None:
        if importlib.util.find_spec("sentence_transformers") is None:
            raise MissingDependencyError(
                "sentence-transformers is required for embedding. Install with `pip install sentence-transformers`."
            )
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name, device=device)
        self.model_name = model_name

    def embed(self, texts: Iterable[str]) -> np.ndarray:
        text_list = list(texts)
        logger.info("Encoding %d texts with %s", len(text_list), self.model_name)
        if importlib.util.find_spec("numpy") is None:
            raise MissingDependencyError("numpy is required for embedding operations.")
        import numpy as np

        return np.array(self.model.encode(text_list, convert_to_numpy=True))

    def embed_query(self, text: str) -> np.ndarray:
        if importlib.util.find_spec("numpy") is None:
            raise MissingDependencyError("numpy is required for embedding operations.")
        import numpy as np

        return np.array(self.model.encode([text], convert_to_numpy=True))[0]
