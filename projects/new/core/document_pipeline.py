import io
import os
import uuid
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Iterable

from PIL import Image
import pytesseract
from pdf2image import convert_from_bytes
import docx

logger = logging.getLogger(__name__)

@dataclass
class Chunk:
    id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class TextExtractor:
    """Extract text for different file types. PDF uses OCR (pytesseract + pdf2image) to support scanned PDFs."""

    def extract(self, file_bytes: bytes, filename: str, content_type: str = None) -> str:
        ext = (filename.split(".")[-1] or "").lower()
        if ext in ("txt", "text"):
            return file_bytes.decode("utf-8", errors="ignore")
        if ext in ("docx",):
            return self._extract_docx(file_bytes)
        if ext in ("pdf",):
            return self._extract_pdf_ocr(file_bytes)
        # fallback: try decode
        return file_bytes.decode("utf-8", errors="ignore")

    def _extract_docx(self, file_bytes: bytes) -> str:
        doc = docx.Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n\n".join(paragraphs)

    def _extract_pdf_ocr(self, file_bytes: bytes, dpi: int = 300) -> str:
        """
        Convert PDF pages to images then run pytesseract OCR.
        Returns combined text.
        """
        pages = convert_from_bytes(file_bytes, dpi=dpi)
        ocr_texts = []
        for i, page in enumerate(pages):
            if page.mode != "RGB":
                page = page.convert("RGB")
            text = pytesseract.image_to_string(page)
            logger.debug("OCR page %d length=%d", i, len(text))
            ocr_texts.append(text)
        return "\n\n".join(ocr_texts)

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
    Character-based chunker with overlap. Replace with token-based chunker for better alignment with LLM tokens.
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

# Lightweight BM25 persistence using rank_bm25 (suitable for small/medium corpora)
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
        import nltk
        try:
            nltk.data.find("tokenizers/punkt")
        except Exception:
            nltk.download("punkt")
        from nltk.tokenize import word_tokenize

        for c in chunks:
            tokens = word_tokenize(c.text.lower())
            self.corpus.append(tokens)
            self.raw_texts.append(c.text)
            self.ids.append(c.id)
        if self.corpus:
            self.bm25 = BM25Okapi(self.corpus)
        self._save()

    def query(self, query_text: str, top_k: int = 10):
        from nltk.tokenize import word_tokenize
        if self.bm25 is None:
            return []
        q_tokens = word_tokenize(query_text.lower())
        scores = self.bm25.get_scores(q_tokens)
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        results = [(self.ids[i], float(scores[i])) for i in top_idx if scores[i] > 0]
        return results

class DocumentIngestor:
    """
    High-level ingestion pipeline:
    - extract (OCR for PDF)
    - normalize
    - chunk (overlap)
    - embed
    - index into vector DB
    - update BM25 index
    """

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
            logger.warning("No text extracted for file %s", filename)
            return []
        file_meta = metadata.copy()
        file_meta.update({"filename": filename})
        chunks = self.chunker.chunk_text(normalized, metadata=file_meta)
        texts = [c.text for c in chunks]
        embeddings = self.embedder.embed_texts(texts)
        self.indexer.add_chunks(chunks, embeddings)
        self.bm25_index.add_documents(chunks)
        return chunks

# application should set default_ingestor at startup with real embedder/indexer instances
default_ingestor = None