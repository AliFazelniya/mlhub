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
    """Represent a text fragment and the metadata required to retrieve it.

    Args:
        id: Unique chunk identifier.
        text: Chunk content.
        metadata: Source metadata for the chunk.
    """
    id: str
    text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class TextExtractor:
    """Extract text from supported uploaded document formats."""

    def extract(self, file_bytes: bytes, filename: str, content_type: str = None) -> str:
        """Extract text from an uploaded file.

        Args:
            file_bytes: Raw file contents.
            filename: Original uploaded filename.
            content_type: Optional MIME type supplied by the caller.

        Returns:
            Extracted text or a decoded fallback representation.
        """
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
        """Extract all text from a DOCX file path.

        Args:
            file_path: Path to the temporary DOCX file.

        Returns:
            Concatenated document text.
        """
        loader = Docx2txtLoader(file_path)
        docs = loader.load()
        return "\n\n".join([doc.page_content for doc in docs])

    def _extract_pdf(self, file_path: str) -> str:
        """Extract all text from a PDF file path.

        Args:
            file_path: Path to the temporary PDF file.

        Returns:
            Concatenated document text.
        """
        loader = PyMuPDFLoader(file_path)
        docs = loader.load()
        return "\n\n".join([doc.page_content for doc in docs])


class TextNormalizer:
    """Basic normalization (whitespace, remove excessive blank lines)"""

    def normalize(self, text: str) -> str:
        """Normalize line endings, whitespace, and excessive blank lines.

        Args:
            text: Raw extracted text.

        Returns:
            Normalized text.
        """
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
        """Initialize chunk boundaries.

        Args:
            chunk_size: Maximum number of characters in a chunk.
            overlap: Number of trailing characters carried into the next chunk.
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    def chunk_text(self, text: str, metadata: Dict[str, Any]) -> List[Chunk]:
        """Split normalized text into overlapping chunks.

        Args:
            text: Text to split.
            metadata: Metadata copied onto each generated chunk.

        Returns:
            Ordered text chunks.
        """
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
        """Initialize and load a persisted BM25 index.

        Args:
            persist_path: Filesystem location of the persisted index.
        """
        self.persist_path = persist_path
        self.corpus = []
        self.raw_texts = []
        self.ids = []
        self.bm25 = None
        self._load()

    def _load(self):
        """Load the persisted BM25 corpus when available."""
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
        """Persist the current BM25 corpus and lookup data."""
        with open(self.persist_path, "wb") as fh:
            pickle.dump({"corpus": self.corpus, "raw_texts": self.raw_texts, "ids": self.ids}, fh)

    def add_documents(self, chunks: Iterable[Chunk]):
        """Tokenize and add chunks to the BM25 corpus.

        Args:
            chunks: Chunks to index.
        """
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
        """Return the highest-scoring BM25 chunk identifiers.

        Args:
            query_text: Text to search for.
            top_k: Maximum number of matches to return.

        Returns:
            Chunk identifier and score tuples.
        """
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
        """Initialize document-processing dependencies.

        Args:
            embedder: Component that creates embeddings.
            indexer: Component that stores vector embeddings.
            bm25_index: Keyword retrieval index.
            chunk_size: Maximum characters per chunk.
            chunk_overlap: Character overlap between chunks.
        """
        self.extractor = TextExtractor()
        self.normalizer = TextNormalizer()
        self.chunker = Chunker(chunk_size, chunk_overlap)
        self.embedder = embedder
        self.indexer = indexer
        self.bm25_index = bm25_index

    def ingest(self, file_bytes: bytes, filename: str, metadata: Dict[str, Any] = None, progress_callback=None) -> List[Chunk]:
        """Extract, normalize, chunk, embed, and index one document.

        Args:
            file_bytes: Raw uploaded file contents.
            filename: Original uploaded filename.
            metadata: Optional document metadata.
            progress_callback: Optional callback receiving progress messages.

        Returns:
            The indexed chunks, or an empty list when no text is extracted.
        """
        def log_progress(msg):
            """Report ingestion progress to the caller and application log.

            Args:
                msg: Progress message to report.
            """
            if progress_callback:
                progress_callback(msg)
            logger.info(msg)

        metadata = metadata or {}

        log_progress("Extracting text from the file...")
        raw_text = self.extractor.extract(file_bytes, filename)


        log_progress("Cleaning and normalizing text...")
        normalized = self.normalizer.normalize(raw_text)
        
        if not normalized:
            logger.warning("No text extracted for file %s. It might be an image-only PDF.", filename)
            return []
            
        file_meta = metadata.copy()
        file_meta.update({"filename": filename})

        log_progress("Chunking the text...")
        chunks = self.chunker.chunk_text(normalized, metadata=file_meta)
        texts = [c.text for c in chunks]

        log_progress(f"Generating AI vectors for {len(chunks)} chunks. (This step is time-consuming)...")
        embeddings = self.embedder.embed_texts(texts)

        log_progress("Saving chunks to the vector database (ChromaDB)...")
        self.indexer.add_chunks(chunks, embeddings)

        log_progress("Updating the keyword search engine (BM25)...")
        self.bm25_index.add_documents(chunks)
        
        logger.info("Successfully ingested %d chunks for file %s", len(chunks), filename)
        return chunks

    def delete_document(self, document_id: int):
        """Remove retrieval data associated with a document.

        Args:
            document_id: Identifier of the document to remove.
        """
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Clearing AI knowledge for document #{document_id}...")

        try:
            if hasattr(self.indexer, '_collection'):
                self.indexer._collection.delete(where={"document_id": document_id})
            elif hasattr(self.indexer, 'delete'):
                self.indexer.delete(where={"document_id": document_id})
            logger.info("Data cleared from ChromaDB.")
        except Exception as e:
            logger.error(f"Error deleting from ChromaDB: {e}")

        try:
            if hasattr(self.bm25_index, 'delete_by_metadata'):
                self.bm25_index.delete_by_metadata(document_id=document_id)
                logger.info("✅ Data cleared from BM25.")
        except Exception as e:
            logger.error(f"❌ Error deleting from BM25: {e}")

default_ingestor = None
