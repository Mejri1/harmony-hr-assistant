import time
from chatbot.chain import get_chatbot_chain
from db.firebase import load_messages
from langchain.memory import ConversationSummaryMemory
from chatbot.memory import get_session_summary ,get_memory_from_session

def load_user_session_resources(user_id, session_id, vectordb, summary=None):
    print(f"[DEBUG] Loading user session resources for user={user_id}, session={session_id}")
    t0 = time.time()

    if summary is None:
        summary = get_session_summary(user_id, session_id)

    memory = get_memory_from_session(user_id, session_id)
    print(f"[DEBUG] Memory loaded: {memory}")
    t1 = time.time()

    messages = load_messages(user_id, session_id)
    t2 = time.time()

    chain = get_chatbot_chain(user_id, session_id, memory=memory, vectordb=vectordb)
    t3 = time.time()

    print(f"[DEBUG] Timing: memory_init={t1-t0:.2f}s, messages_load={t2-t1:.2f}s, chain_init={t3-t2:.2f}s")
    return chain, messages
