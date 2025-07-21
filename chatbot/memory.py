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

def get_incremental_summary(user_id: str, session_id: str, chunk_size: int = 1024) -> str:
    """
    Generate a full summary of a session using BART with chunked input to avoid truncation.
    - Loads all messages from the session.
    - Constructs a 'User: ... Harmony: ...' format.
    - Splits the conversation into chunks to stay under the model limit.
    - Summarizes each chunk individually, then merges summaries.
    Uses adaptive min_length and max_length based on input size.
    """
    messages_data = load_messages(user_id, session_id) or []
    print(f"[DEBUG] Messages data: {messages_data}")

    # Format the conversation as alternating lines of user/bot messages
    conversation_text = ""
    for msg in messages_data:
        if msg["sender"] == "user":
            conversation_text += f"User: {msg['content']}\n"
        elif msg["sender"] == "bot":
            conversation_text += f"chatbot: {msg['content']}\n"

    print(f"[DEBUG] Full conversation text length: {len(conversation_text)}")

    # Split the conversation into chunks of appropriate size
    chunks = [conversation_text[i:i + chunk_size] for i in range(0, len(conversation_text), chunk_size)]
    print(f"[DEBUG] Split into {len(chunks)} chunks.")

    # Summarize each chunk individually with adaptive min/max length
    summaries = []
    for i, chunk in enumerate(chunks):
        input_len = len(chunk.split())
        min_len = max(20, int(0.3 * input_len))
        max_len = max(50, int(0.6 * input_len))
        print(f"[DEBUG] Summarizing chunk {i+1}/{len(chunks)} (input words: {input_len}, min_len: {min_len}, max_len: {max_len})")
        summary = summarizer(chunk, max_length=max_len, min_length=min_len, do_sample=False)[0]['summary_text']
        summaries.append(summary)

    # Join all partial summaries into one final summary
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
