# core/apps.py (inside AppConfig.ready)
from django.apps import AppConfig
import os

class CoreConfig(AppConfig):
    name = "core"

    def ready(self):
        try:
            from .document_pipeline import default_ingestor, DocumentIngestor, BM25Index
            from .embedder import EmbedderWrapper
            from .retrieval import ChromaIndexer

            chroma_dir = os.environ.get("CHROMA_PERSIST_DIR", os.path.join(os.path.dirname(__file__), "..", "chroma_db"))
            bm25_path = os.environ.get("BM25_PERSIST_PATH", "/tmp/bm25_index.pkl")

            embedder = EmbedderWrapper(model_name="all-MiniLM-L6-v2")
            chroma_indexer = ChromaIndexer(chroma_persist_dir=chroma_dir)
            bm25 = BM25Index(persist_path=bm25_path)

            # create and assign to module-level variable
            from . import document_pipeline as dp_mod
            dp_mod.default_ingestor = DocumentIngestor(embedder=embedder, indexer=chroma_indexer, bm25_index=bm25)
        except Exception as exc:
            import logging
            logging.getLogger(__name__).exception("Failed to initialize default_ingestor: %s", exc)