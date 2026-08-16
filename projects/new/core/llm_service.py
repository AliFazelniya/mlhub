import os
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from .vector_store import search_similar_chunks
from .models import QAHistory

# Setup logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_robust_llm():
    api_key = os.environ.get("OPENROUTER_API_KEY")
    base_url = "https://openrouter.ai/api/v1"
    
    primary_llm = ChatOpenAI(model="google/gemma-4-26b-a4b-it:free", api_key=api_key, base_url=base_url)
    
    fallback_1 = ChatOpenAI(model="openai/gpt-oss-20b:free", api_key=api_key, base_url=base_url)
    fallback_2 = ChatOpenAI(model="nvidia/nemotron-3-ultra-550b-a55b:free", api_key=api_key, base_url=base_url)
    fallback_3 = ChatOpenAI(model="nvidia/nemotron-3-nano-30b-a3b:free", api_key=api_key, base_url=base_url)
    
    robust_llm = primary_llm.with_fallbacks([fallback_1, fallback_2, fallback_3])
    return robust_llm

def generate_answer(question: str) -> str:
    logger.info(f"Received new request for processing. Question: {question}")
    
    prompt = PromptTemplate(
        template = "Answer the following question based on the provided context:\n\nContext:\n{context}\n\nQuestion: {question}",
        input_variables = ["context", "question"]
    )
    
    try:
        llm = get_robust_llm()
        chain = prompt | llm
        
        logger.info("Searching for relevant chunks in ChromaDB...")
        relevant_chunks = search_similar_chunks(question, k=3)
        context = "\n\n---\n\n".join([chunk.page_content for chunk in relevant_chunks])
        
        logger.info(f"Context length extracted: {len(context)}")
    
        if not context.strip():
            answer = "There is no relevant information in the documents to answer your question."
            logger.info("No relevant context found. Returning default fallback answer.")
        else:
            logger.info("Sending request to OpenRouter (with fallback support)...")
            response = chain.invoke({"context": context, "question": question})
            answer = response.content
            logger.info("Successfully received response from the model.")

        logger.info("Saving QA interaction to database.")
        QAHistory.objects.create(question=question, answer=answer)
        
        return answer
        
    except Exception as e:
        logger.error(f"Critical error communicating with LLM API: {str(e)}")
        raise e