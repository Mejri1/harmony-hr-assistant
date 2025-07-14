# db/vectorstore.py

import os
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

CHROMA_PATH = r"C:\Users\Omar\Desktop\ai-attrition-system\db\chroma"

def get_vectorstore():
    embedder = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedder)
    return vectordb
