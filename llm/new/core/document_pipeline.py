import io
import os
import uuid
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Iterable
import tempfile

from langchain_community.document_loaders import PyMuPDFLoader, Docx2txtLoader
import docx

logger = logging.getLogger(__name__)

@dataclass
class Chunk:
    id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class TextExtractor:
    """Extract text using fast, modern LangChain loaders optimized for Persian."""

    def extract(self, file_bytes: bytes, filename: str, content_type: str = None) -> str:
        ext = (filename.split(".")[-1] or "").lower()
        
        if ext in ("txt", "text"):
            return file_bytes.decode("utf-8", errors="ignore")
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{ext}") as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name

        try:
            if ext in ("docx",):
                return self._extract_docx(temp_file_path)
            if ext in ("pdf",):
                return self._extract_pdf(temp_file_path)
        finally:
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                
        # fallback
        return file_bytes.decode("utf-8", errors="ignore")

    def _extract_docx(self, file_path: str) -> str:
        loader = Docx2txtLoader(file_path)
        docs = loader.load()
        return "\n\n".join([doc.page_content for doc in docs])

    def _extract_pdf(self, file_path: str) -> str:
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
        return "\n\n".join([doc.page_content for doc in docs])


class TextNormalizer:
    """Basic normalization (whitespace, remove excessive blank lines)"""

    def normalize(self, text: str) -> str:
        import re
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"\n{3,}", "\n\n", text)
        lines = [ln.strip() for ln in text.splitlines()]
        lines = [ln for ln in lines if ln != ""]
        normalized = "\n".join(lines)
        return normalized.strip()

class Chunker:
    """
    Character-based chunker with overlap. 
    """

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        chunks = []
        start = 0
        text_len = len(text)
        while start < text_len:
            end = min(start + self.chunk_size, text_len)
            chunk_text = text[start:end]
            chunk_id = str(uuid.uuid4())
            chunk_meta = metadata.copy()
            chunk_meta.update({"source_offset": start, "source_length": len(chunk_text)})
            chunks.append(Chunk(id=chunk_id, text=chunk_text, metadata=chunk_meta))
            if end == text_len:
                break
            start = end - self.overlap
        return chunks

# Lightweight BM25 persistence using rank_bm25 
# Lightweight BM25 persistence using rank_bm25 
import pickle
from rank_bm25 import BM25Okapi

class BM25Index:
    def __init__(self, persist_path: str = "/tmp/bm25_index.pkl"):
        self.persist_path = persist_path
        self.corpus = []
        self.raw_texts = []
        self.ids = []
        self.bm25 = None
        self._load()

    def _load(self):
        if os.path.exists(self.persist_path):
            try:
                with open(self.persist_path, "rb") as fh:
                    data = pickle.load(fh)
                    self.corpus = data["corpus"]
                    self.raw_texts = data["raw_texts"]
                    self.ids = data["ids"]
                    if self.corpus:
                        self.bm25 = BM25Okapi(self.corpus)
            except Exception:
                logger.exception("Failed to load BM25 index, starting fresh.")

    def _save(self):
        with open(self.persist_path, "wb") as fh:
            pickle.dump({"corpus": self.corpus, "raw_texts": self.raw_texts, "ids": self.ids}, fh)

    def add_documents(self, chunks: Iterable[Chunk]):
        try:
            import nltk
            nltk.data.find("tokenizers/punkt")
            nltk.data.find("tokenizers/punkt_tab")
            from nltk.tokenize import word_tokenize
            tokenize_fn = lambda t: word_tokenize(t.lower())
        except Exception:
            logger.warning("NLTK packages missing! Falling back to fast whitespace tokenization.")
            tokenize_fn = lambda t: t.lower().split()

        for c in chunks:
            tokens = tokenize_fn(c.text)
            self.corpus.append(tokens)
            self.raw_texts.append(c.text)
            self.ids.append(c.id)
            
        if self.corpus:
            self.bm25 = BM25Okapi(self.corpus)
        self._save()

    def query(self, query_text: str, top_k: int = 10):
        if self.bm25 is None:
            return []
            
        try:
            import nltk
            nltk.data.find("tokenizers/punkt")
            nltk.data.find("tokenizers/punkt_tab")
            from nltk.tokenize import word_tokenize
            q_tokens = word_tokenize(query_text.lower())
        except Exception:
            q_tokens = query_text.lower().split()
            
        scores = self.bm25.get_scores(q_tokens)
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        results = [(self.ids[i], float(scores[i])) for i in top_idx if scores[i] > 0]
        return results

class DocumentIngestor:
    def __init__(self, embedder, indexer, bm25_index: BM25Index, chunk_size=1000, chunk_overlap=200):
        self.extractor = TextExtractor()
        self.normalizer = TextNormalizer()
        self.chunker = Chunker(chunk_size, chunk_overlap)
        self.embedder = embedder
        self.indexer = indexer
        self.bm25_index = bm25_index

    def ingest(self, file_bytes: bytes, filename: str, metadata: Dict[str, Any] = None) -> List[Chunk]:
        metadata = metadata or {}
        

        raw_text = self.extractor.extract(file_bytes, filename)
        
    
        normalized = self.normalizer.normalize(raw_text)
        
        if not normalized:
            logger.warning("No text extracted for file %s. It might be an image-only PDF.", filename)
            return []
            
        file_meta = metadata.copy()
        file_meta.update({"filename": filename})
        
        chunks = self.chunker.chunk_text(normalized, metadata=file_meta)
        texts = [c.text for c in chunks]
        
        embeddings = self.embedder.embed_texts(texts)
        self.indexer.add_chunks(chunks, embeddings)
        self.bm25_index.add_documents(chunks)
        
        logger.info("Successfully ingested %d chunks for file %s", len(chunks), filename)
        return chunks

default_ingestor = None