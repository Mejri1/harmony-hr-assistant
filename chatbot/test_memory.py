import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from chatbot.memory import get_memory_from_session

user_id = "REPLACE_WITH_UID"
session_id = "hgAcJ3zgmM3sWBUscA7x"

memory = get_memory_from_session(user_id, session_id)

for msg in memory.chat_memory.messages:
    print(f"[{msg.type}] {msg.content}")
