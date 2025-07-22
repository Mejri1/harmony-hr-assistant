# The summarization model is loaded ONCE at startup (global scope) to avoid latency on first use.
from transformers import pipeline
from db.firebase import load_session_summary, load_messages
from langchain.schema import AIMessage, HumanMessage
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationSummaryMemory
from operator import itemgetter

# --- Summarization Pipeline ---
# Load the model ONCE at startup to avoid latency later
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

from transformers import pipeline

# Initialize the summarization pipeline once (outside the function if possible)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

import requests
from typing import List

def call_llm_summary(prompt: str) -> str:
    """
    Send the prompt to the local LLM API for summarization.
    """
    url = "http://127.0.0.1:1234/v1/chat/completions"
    headers = {"Content-Type": "application/json"}
    payload = {
        "model": "mistralai/Mistral-7B-Instruct-v0.1",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant that summarizes conversations."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 512
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

def get_incremental_summary(user_id: str, session_id: str, chunk_size: int = 2000) -> str:
    """
    Summarize a full conversation session using a local LLM by chunking the data.
    """
    messages_data = load_messages(user_id, session_id) or []
    print(f"[DEBUG] Messages data: {messages_data}")

    # Format conversation text
    conversation_text = ""
    for msg in messages_data:
        if msg["sender"] == "user":
            conversation_text += f"User: {msg['content']}\n"
        elif msg["sender"] == "bot":
            conversation_text += f"Chatbot: {msg['content']}\n"

    print(f"[DEBUG] Full conversation text length: {len(conversation_text)}")

    # Split into manageable chunks
    chunks = [conversation_text[i:i + chunk_size] for i in range(0, len(conversation_text), chunk_size)]
    print(f"[DEBUG] Split into {len(chunks)} chunks")

    summaries: List[str] = []
    for i, chunk in enumerate(chunks):
        prompt = f"Summarize the following conversation:\n\n{chunk}"
        print(f"[DEBUG] Summarizing chunk {i+1}/{len(chunks)} (length: {len(chunk)} characters)")
        try:
            summary = call_llm_summary(prompt)
            summaries.append(summary)
        except Exception as e:
            print(f"[ERROR] Failed to summarize chunk {i+1}: {e}")

    final_summary = " ".join(summaries)
    print(f"[DEBUG] Final summary length: {len(final_summary)}")
    return final_summary



# --- Guidance for Usage ---
"""
Best practice for summarization with facebook/bart-large-cnn:
- Do NOT summarize after every message.
- Summarize after every K messages (e.g., K=10), or when a session ends, or when a token/character limit is reached.
- Store the summary and only summarize the new messages since the last summary, appending or replacing as needed.
- This is efficient and maintains summary quality.
"""

# --- Get chat history for a session ---

def get_memory_from_session(user_id: str, session_id: str):
    print(f"[DEBUG] get memory from session {user_id} {session_id}")
    summary = load_session_summary(user_id, session_id) or ""

    llm = ChatOpenAI(
        temperature=0.0,
        model="gpt-3.5-turbo",
        base_url="http://127.0.0.1:1234/v1",
        api_key="not-needed"
    )

    memory = ConversationSummaryMemory(
        llm=llm,
        return_messages=True,
        memory_key="history"
    )

    # Directly inject the summary
    if summary:
        memory.buffer = summary
        print(f"[DEBUG] Injected summary into memory buffer (length={len(summary)})")

    return memory
