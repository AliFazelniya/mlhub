import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from .vector_store import search_similar_chunks
from .models import QAHistory
llm = ChatOpenAI(
    api_key=os.environ.get("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="google/gemma-4-31b-it:free", 
)

PROMPT_TEMPLATE = """
تو یک دستیار هوشمند پاسخگویی به سوالات از روی اسناد هستی.
با استفاده از متن‌های فراهم شده در بخش "متن مرجع"، به سوال کاربر پاسخ دقیق و کامل بده.
اگر پاسخ سوال در متن مرجع وجود نداشت، فقط بگو: "متاسفانه اطلاعاتی در این باره در اسناد یافت نشد." و از خودت چیزی حدس نزن.

متن مرجع:
{context}

سوال کاربر: {question}

پاسخ تو:
"""

prompt = PromptTemplate(template=PROMPT_TEMPLATE, input_variables=["context", "question"])
chain = prompt | llm

def generate_answer(question):
    relevant_chunks = search_similar_chunks(question, k=3)
    
    context = "\n\n---\n\n".join([chunk.page_content for chunk in relevant_chunks])
    
    if not context:
        answer = "there is no relevant information in the documents to answer your question."
    else:
        response = chain.invoke({"context": context, "question": question})
        answer = response.content
    
    QAHistory.objects.create(question=question, answer=answer)
    
    return answer
