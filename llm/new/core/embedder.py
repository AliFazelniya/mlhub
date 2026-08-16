
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np

class EmbedderWrapper:
    """
    Thin wrapper over sentence-transformers for local embeddings.
    Alternatively replace with remote embedding API (OpenRouter/OpenAI) if preferred.
    """

    def __init__(self, model_name: str = "/app/all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        # returns list of vectors (floats)
        embs = self.model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        # ensure list-of-lists
        return [list(map(float, vec)) for vec in embs]