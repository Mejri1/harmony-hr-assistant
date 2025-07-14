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

def summarize_conversation(prev_summary: str, new_messages: list, max_input_length=1024) -> str:
    """
    Summarize the conversation using facebook/bart-large-cnn.
    Only summarize the previous summary + new messages.
    """
    # Format input as: Existing summary + New exchange
    conversation_text = f"Existing summary: {prev_summary}\n\nNew exchange:\n"
    for msg in new_messages:
        sender = "You" if msg["sender"] == "user" else "Bot"
        conversation_text += f"{sender}: {msg['text']}\n"
    conversation_text = conversation_text[-max_input_length:]
    summary = summarizer(conversation_text, max_length=150, min_length=30, do_sample=False)[0]['summary_text']
    return summary

def get_incremental_summary(user_id: str, session_id: str, k: int = 10) -> str:
    """
    Generate or update the summary for a session using BART.
    Summarizes every k messages.
    """
    prev_summary = load_session_summary(user_id, session_id) or ""
    messages_data = load_messages(user_id, session_id) or []

    if len(messages_data) <= k:
        new_messages = messages_data
    else:
        new_messages = messages_data[-k:]

    summary = summarize_conversation(prev_summary, new_messages)
    return summary

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
    messages_data = load_messages(user_id, session_id) or []
    summary = load_session_summary(user_id, session_id) or ""

    # Sort messages chronologically using timestamp
    messages_data.sort(key=itemgetter("timestamp"))

    # Use a dummy or actual LLM endpoint for LangChain memory summarization
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

    # Hydrate memory from message pairs
    for i in range(0, len(messages_data), 2):
        user_msg = messages_data[i]["content"] if messages_data[i]["sender"] == "user" else ""
        bot_msg = (
            messages_data[i + 1]["content"]
            if i + 1 < len(messages_data) and messages_data[i + 1]["sender"] == "bot"
            else ""
        )
        if user_msg or bot_msg:
            memory.save_context({"input": user_msg}, {"output": bot_msg})

    return memory
