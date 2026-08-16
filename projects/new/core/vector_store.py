import os
from django.conf import settings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

CHROMA_PERSIST_DIR = os.path.join(settings.BASE_DIR, 'chroma_db')

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vector_store = Chroma(
    collection_name="documents",
    embedding_function=embeddings,
    persist_directory=CHROMA_PERSIST_DIR
)

def process_and_store_document(doc_id: int, text: str, title: str):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = text_splitter.split_text(text)
    
    metadatas = [{"doc_id": doc_id, "source": title} for _ in chunks]
    
    vector_store.add_texts(texts=chunks, metadatas=metadatas)

def search_similar_chunks(query, k=3):
    return vector_store.similarity_search(query, k=k)