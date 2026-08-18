"""Local embedding utilities."""

from typing import List

import numpy as np
from sentence_transformers import SentenceTransformer


class EmbedderWrapper:
    """Wrap a SentenceTransformer model for local text embedding.

    Args:
        model_name: The local path or model identifier to load.
    """

    def __init__(self, model_name: str = "/app/all-MiniLM-L6-v2"):
        """Initialize the sentence-transformer model.

        Args:
            model_name: The local path or model identifier to load.
        """
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate floating-point embedding vectors for text inputs.

        Args:
            texts: Text strings to encode.

        Returns:
            A list containing one vector for each input text.
        """
        # Convert NumPy output to plain floats for downstream serialization.
        embs = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return [list(map(float, vec)) for vec in embs]
