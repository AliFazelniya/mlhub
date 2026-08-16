import os
import logging
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from .vector_store import search_similar_chunks
from .models import QAHistory

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class DocumentAssistant:
    def __init__(self):
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=False
        )
        self.llm = self._get_robust_llm()
        logger.info("DocumentAssistant initialized with Memory.")

    def _get_robust_llm(self):
        api_key = os.environ.get("OPENROUTER_API_KEY")
        base_url = "https://openrouter.ai/api/v1"
        
        primary_llm = ChatOpenAI(model="google/gemma-4-31b-it:free", api_key=api_key, base_url=base_url)
        
        fallback_1 = ChatOpenAI(model="meta-llama/llama-3.1-8b-instruct:free", api_key=api_key, base_url=base_url)
        fallback_2 = ChatOpenAI(model="nvidia/nemotron-nano-9b-v2:free", api_key=api_key, base_url=base_url)
        fallback_3 = ChatOpenAI(model="qwen/qwen-2-7b-instruct:free", api_key=api_key, base_url=base_url)
        
        return primary_llm.with_fallbacks([fallback_1, fallback_2, fallback_3])

    def generate_answer(self, question: str) -> dict:
        logger.info(f"Received new conversational request. Question: {question}")
        
        try:
            logger.info("Searching for relevant chunks in ChromaDB...")
            relevant_chunks = search_similar_chunks(question, k=3)
            context = "\n\n---\n\n".join([chunk.page_content for chunk in relevant_chunks])

            sources = list(set([chunk.metadata.get("source", "Unknown Document") for chunk in relevant_chunks]))
            

            if not context.strip():
                answer = "I'm sorry, I couldn't find relevant information in the uploaded documents to answer your question."
                sources = []
            else:
                logger.info("Sending conversational request to OpenRouter...")
                
                prompt_template = """You are an intelligent AI assistant. 
Use the following context from uploaded documents and the chat history to answer the user's question. 
If the answer is not contained in the context, clearly state that you don't know. Do not hallucinate.

Context: 
{context}

Chat History: 
{chat_history}

Human: {question}
Assistant:"""
                
                prompt = PromptTemplate(
                    template=prompt_template,
                    input_variables=["context", "chat_history", "question"]
                )
                
                history_vars = self.memory.load_memory_variables({})
                chat_history = history_vars.get("chat_history", "")
                

                chain = prompt | self.llm
                response = chain.invoke({
                    "context": context,
                    "chat_history": chat_history,
                    "question": question
                })
                
                answer = response.content
                

                self.memory.save_context({"input": question}, {"output": answer})
                logger.info("Successfully received response and updated memory.")

            # 3. Save to Django Database
            logger.info("Saving QA interaction to database.")
            QAHistory.objects.create(question=question, answer=answer)
            
            # Return dictionary with answer and sources
            return {"answer": answer, "sources": sources}
            
        except Exception as e:
            logger.error(f"Critical error communicating with LLM API: {str(e)}")
            raise e

assistant = DocumentAssistant()

def generate_answer(question: str) -> dict:
    return assistant.generate_answer(question)