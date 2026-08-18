import time
import logging
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import chromadb
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

logger = logging.getLogger(__name__)

@dataclass
class DocumentChunk:
    """Represent a retrieved document chunk and its relevance score.

    Args:
        id: Unique chunk identifier.
        text: Chunk text.
        metadata: Source metadata.
        score: Retrieval score.
    """
    id: str
    text: str
    metadata: Dict[str, Any]
    score: float = 0.0

class ChromaIndexer:
    """
    Thin wrapper around chromadb client for indexing and vector search.
    Uses a collection named 'documents'.
    """

    def __init__(self, chroma_persist_dir: str = None):
        """Initialize the Chroma client and documents collection.

        Args:
            chroma_persist_dir: Optional path for persistent Chroma storage.
        """
        if chroma_persist_dir:
            self.client = chromadb.PersistentClient(path=chroma_persist_dir)
        else:
            self.client = chromadb.Client()
            
        self.collection_name = "documents"
        self.collection = self.client.get_or_create_collection(name=self.collection_name)

    def add_chunks(self, chunks: List, embeddings: List[List[float]]):
        """Add chunks and their embeddings to the Chroma collection.

        Args:
            chunks: Chunks to store.
            embeddings: Embedding vectors aligned with chunks.
        """
        ids = [c.id for c in chunks]
        metadatas = [c.metadata for c in chunks]
        documents = [c.text for c in chunks]
        self.collection.add(ids=ids, metadatas=metadatas, documents=documents, embeddings=embeddings)

    def query_vector(self, query_embedding: List[float], top_k: int = 10, metadata_filter: dict = None):
        """Query Chroma for chunks nearest to an embedding.

        Args:
            query_embedding: Vector representation of the query.
            top_k: Maximum number of matches.
            metadata_filter: Optional Chroma metadata filter.

        Returns:
            Retrieved document chunks.
        """
    
        query_kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
        }
        
        if metadata_filter:
            query_kwargs["where"] = metadata_filter

        results = self.collection.query(**query_kwargs)
        
        res = []
        if results and results.get("ids") and len(results["ids"]) > 0:
            for idx, chid in enumerate(results["ids"][0]):
                res.append(
                    DocumentChunk(
                        id=chid,
                        text=results["documents"][0][idx],
                        metadata=results["metadatas"][0][idx] if results.get("metadatas") else {},
                        score=float(results["distances"][0][idx]) if results.get("distances") and results["distances"][0][idx] is not None else 0.0
                    )
                )
        return res

class HybridRetriever:
    """
    Combines Chroma vector retrieval and BM25 keyword retrieval (BM25Index).
    """

    def __init__(self, chroma_indexer: ChromaIndexer, bm25_index, embedder):
        """Initialize vector and keyword retrieval dependencies.

        Args:
            chroma_indexer: Vector index interface.
            bm25_index: Keyword index interface.
            embedder: Component that embeds query text.
        """
        self.chroma = chroma_indexer
        self.bm25 = bm25_index
        self.embedder = embedder

    def retrieve(self, query: str, top_k_vector: int = 10, top_k_bm25: int = 10, metadata_filter: dict = None) -> Tuple[List[DocumentChunk], int]:
        """Retrieve and merge vector and BM25 candidates.

        Args:
            query: User query text.
            top_k_vector: Vector candidates to retrieve.
            top_k_bm25: Keyword candidates to retrieve.
            metadata_filter: Optional vector-search metadata filter.

        Returns:
            Merged chunks and elapsed retrieval time in milliseconds.
        """
        t0 = time.time()
        q_emb = self.embedder.embed_texts([query])[0]
        vector_results = self.chroma.query_vector(q_emb, top_k=top_k_vector, metadata_filter=metadata_filter)

        bm25_hits = self.bm25.query(query, top_k=top_k_bm25)
        bm25_ids = [hid for hid, _score in bm25_hits]

        bm25_docs = []
        if bm25_ids:
            docs = self.chroma.collection.get(ids=bm25_ids)
            if docs and docs.get("ids"):
                for idx, cid in enumerate(docs["ids"]):
                    bm25_docs.append(
                        DocumentChunk(
                            id=cid,
                            text=docs["documents"][idx],
                            metadata=docs["metadatas"][idx] if docs.get("metadatas") else {},
                            score=float(bm25_hits[idx][1]) if idx < len(bm25_hits) else 0.0
                        )
                    )

        # Deduplicate chunks while retaining the highest score per identifier.
        merged = {}
        for d in vector_results + bm25_docs:
            if d.id not in merged or d.score > merged[d.id].score:
                merged[d.id] = d

        merged_list = list(merged.values())
        merged_list.sort(key=lambda d: d.score, reverse=True)
        elapsed = int((time.time() - t0) * 1000.0)
        return merged_list, elapsed

class CrossEncoderReranker:
    """
    Uses a HuggingFace cross-encoder model to score (query, doc) pairs.
    Default model: lightweight cross-encoder good for reranking.
    """

    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2", device: str = None):
        """Load the cross-encoder model on the selected device.

        Args:
            model_name: HuggingFace model identifier.
            device: Optional Torch device override.
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_name).to(self.device)
        self.model.eval()

    def rerank(self, query: str, candidates: List[DocumentChunk], top_n: int = 5) -> List[tuple]:
        """Score candidate chunks against a query and return the top results.

        Args:
            query: User query text.
            candidates: Candidate chunks to score.
            top_n: Maximum number of reranked candidates to return.

        Returns:
            Candidate and score tuples ordered by descending relevance.
        """
        if not candidates:
            return []
            
        pairs = [(query, c.text) for c in candidates]
        scores = []
        batch_size = 16
        with torch.no_grad():
            for i in range(0, len(pairs), batch_size):
                batch = pairs[i : i + batch_size]
                inputs = self.tokenizer([q for q, _ in batch], [d for _, d in batch],
                                        padding=True, truncation=True, return_tensors="pt").to(self.device)
                outputs = self.model(**inputs)
                logits = outputs.logits.squeeze(-1).cpu().numpy()
                if logits.ndim == 0:
                    logits = np.array([float(logits)])
                scores.extend([float(x) for x in logits])

        scored = [(candidates[i], scores[i]) for i in range(len(candidates))]
        scored.sort(key=lambda p: p[1], reverse=True)
        return scored[:top_n]
