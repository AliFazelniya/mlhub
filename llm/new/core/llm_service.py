import time
import logging
from typing import Dict, Any
import os 
from langchain_core.prompts import PromptTemplate
from .retrieval import HybridRetriever, CrossEncoderReranker, ChromaIndexer
from .embedder import EmbedderWrapper
from .llm_wrappers import LLMFactory
from .document_pipeline import BM25Index, DocumentIngestor
from .models import QAHistory

logger = logging.getLogger(__name__)

STRICT_PROMPT_TEMPLATE = """
You are a highly precise information retrieval assistant. 
You MUST answer strictly using ONLY the provided context chunks below. Do NOT use any external knowledge, do NOT speculate, and do NOT invent facts.

CRITICAL INSTRUCTION: You MUST answer in the EXACT SAME LANGUAGE as the user's question (e.g., if the user asks in Persian, you MUST reply in natural and fluent Persian).

If the answer cannot be fully derived from the provided context, respond exactly and only with:
اطلاعات کافی در مستندات شما برای پاسخ به این سوال پیدا نشد.

Context:
{context}

Question:
{question}

Answer (Clear, concise, and in the user's language, without any raw JSON or metadata attached):
"""

# Build the runtime components (singletons). In production, wire these in better (Django AppConfig.ready)
CHROMA_PERSIST_DIR = os.environ.get("CHROMA_PERSIST_DIR", os.path.join(os.path.dirname(__file__), "..", "chroma_db"))
_embedder = EmbedderWrapper(model_name="/app/all-MiniLM-L6-v2") # تنظیم شده روی پوشه لوکال شما
_chroma_indexer = ChromaIndexer(chroma_persist_dir=CHROMA_PERSIST_DIR)
_bm25 = BM25Index(persist_path=os.environ.get("BM25_PERSIST_PATH", "/tmp/bm25_index.pkl"))
_reranker = CrossEncoderReranker(model_name="cross-encoder/ms-marco-MiniLM-L-6-v2")
_retriever = HybridRetriever(chroma_indexer=_chroma_indexer, bm25_index=_bm25, embedder=_embedder)
_llm_factory = LLMFactory()

# Provide a generate_answer function used by existing views for compatibility
def generate_answer(question: str) -> Dict[str, Any]:
    """
    Compatibility wrapper used by views and external callers — returns dict with 'answer' and 'sources'.
    Also logs telemetry to QAHistory.
    """
    service = LLMService(_retriever, _reranker, _llm_factory)
    result = service.answer(question)
    
    # For compatibility with previous API: return {"answer": ..., "sources": [...]}
    sources = []
    for chunk_id, meta in (result.get("citations") or {}).items():
        sources.append(meta.get("filename") or meta.get("title") or "Unknown")
        
    return {
        "answer": result.get("answer_text", ""), 
        "sources": list(set(sources)),
        "telemetry": result.get("telemetry", {})
    }

class LLMService:
    def __init__(self, retriever: HybridRetriever, reranker: CrossEncoderReranker, llm_factory: LLMFactory, chunk_context_window: int = 3):
        self.retriever = retriever
        self.reranker = reranker
        self.llm_factory = llm_factory
        self.chunk_context_window = chunk_context_window

    def answer(self, query: str, user_meta: dict = None, metadata_filter: dict = None) -> Dict[str, Any]:
        user_meta = user_meta or {}
        qa = QAHistory.objects.create(query_text=query, status="processing")
        
        try:
            # 1. Hybrid Retrieval (Vector + Keyword)
            candidates, retrieval_latency_ms = self.retriever.retrieve(query, top_k_vector=10, top_k_bm25=10, metadata_filter=metadata_filter)
            top_candidates_raw = candidates[:10]
            
            # 2. Re-ranking using CrossEncoder
            reranked = self.reranker.rerank(query, top_candidates_raw, top_n=self.chunk_context_window * 2)

            final_k = min(self.chunk_context_window, len(reranked))
            selected = reranked[:final_k]
            selected_chunks = [c for c, score in selected]
            selected_ids = [c.id for c in selected_chunks]

            context_parts = []
            chunk_map = {}
            for (chunk, rscore) in selected:
                context_parts.append(f"[{chunk.id}]\n{chunk.text}\n")
                chunk_map[chunk.id] = {
                    "filename": chunk.metadata.get("filename") or chunk.metadata.get("title"),
                    "source_offset": chunk.metadata.get("source_offset"),
                    "score": getattr(chunk, "score", None),
                    "rerank_score": float(rscore), # تبدیل به float برای سازگاری با JSON
                }
            context = "\n\n---\n\n".join(context_parts)

            # 3. Prompt Setup
            prompt_template = PromptTemplate(input_variables=["context", "question"], template=STRICT_PROMPT_TEMPLATE)
            llm_models_to_try = self.llm_factory.get_candidate_model_names()
            llm_exception = None
            answer_text = None
            used_model_name = None

            # 4. LLM Execution with Fallbacks
            for model_name in llm_models_to_try:
                try:
                    llm = self.llm_factory.get_llm(model_name)
                    chain = prompt_template | llm
                    
                    t0 = time.time()
                    response = chain.invoke({
                        "context": context, 
                        "question": query,
                    })
                    
                    answer_text = response.content
                    used_model_name = model_name
                    break
                except Exception as exc:
                    logger.exception("LLM model %s failed: %s", model_name, exc)
                    llm_exception = exc
                    continue

            # 5. Handle All Models Failed
            if not answer_text:
                qa.status = "failed"
                qa.error_text = str(llm_exception) if llm_exception else "No model produced an answer"
                qa.save()
                return {"answer_text": "", "citations": {}, "telemetry": {"status": "failed", "error": qa.answer}}

            # 6. Anti-Hallucination Check
            if answer_text.strip() == "Insufficient information in the provided documents.":
                qa.status = "insufficient_info"
            else:
                qa.status = "success"

            # 7. Update Telemetry & Save
            qa.response_text = answer_text
            qa.retrieval_latency_ms = retrieval_latency_ms
            qa.selected_chunk_ids = selected_ids
            qa.chunk_score_map = chunk_map
            qa.llm_model = used_model_name
            qa.save()

            telemetry = {
                "retrieval_latency_ms": retrieval_latency_ms,
                "selected_chunk_ids": selected_ids,
                "chunk_score_map": chunk_map,
                "llm_model": used_model_name,
                "status": qa.status,
            }

            citations = {cid: chunk_map[cid] for cid in selected_ids}
            return {"answer_text": answer_text, "citations": citations, "telemetry": telemetry}

        except Exception as exc:
            logger.exception("LLMService.answer failed: %s", exc)
            qa.status = "failed"
            qa.error_text = str(exc)
            qa.save()
            return {"answer_text": "", "citations": {}, "telemetry": {"status": "failed", "error": str(exc)}}