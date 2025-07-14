import os
import re
import string
from langchain_community.vectorstores import Chroma
from langchain_community.document_loaders import TextLoader, PyPDFLoader
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

CHROMA_PATH = "db/chroma"
PDF_DIR = os.path.join("data")
MARKDOWN_DIR = os.path.join("data", "markdown")

def preprocess_text(text):
    text = text.lower()
    text = ''.join(ch for ch in text if ch in string.printable)
    text = re.sub(r'[^\w\s.,;:!?-]', '', text)
    text = ' '.join(text.strip().split())
    return text

def load_documents(markdown_folder, pdf_folder):
    docs = []
    # Load markdown files
    for filename in os.listdir(markdown_folder):
        if filename.endswith(".md"):
            filepath = os.path.join(markdown_folder, filename)
            loader = TextLoader(filepath, encoding="utf-8")
            loaded_docs = loader.load()
            for doc in loaded_docs:
                doc.page_content = preprocess_text(doc.page_content)
            docs.extend(loaded_docs)
    # Load PDF files
    for filename in os.listdir(pdf_folder):
        if filename.endswith(".pdf"):
            filepath = os.path.join(pdf_folder, filename)
            loader = PyPDFLoader(filepath)
            loaded_docs = loader.load()
            for doc in loaded_docs:
                doc.page_content = preprocess_text(doc.page_content)
            docs.extend(loaded_docs)
    return docs

def split_documents(docs):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=150
    )
    return splitter.split_documents(docs)

def embed_and_store(chunks):
    embedder = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embedder,
        persist_directory=CHROMA_PATH
    )
    vectordb.persist()
    return vectordb

def build_vectorstore():
    print("📄 Loading markdown and PDF files...")
    docs = load_documents(MARKDOWN_DIR, PDF_DIR)
    
    print("🔪 Splitting into chunks...")
    chunks = split_documents(docs)
    
    print("🧠 Embedding and saving to Chroma...")
    vectordb = embed_and_store(chunks)

    print("✅ Vector store is ready!")
    return vectordb

if __name__ == "__main__":
    build_vectorstore()
