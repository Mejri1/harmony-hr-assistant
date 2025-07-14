import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.firebase import create_session, save_message, load_session_history

# Replace with a real user ID (from login)
user_id = "75D0JflqF3Rx40E9vSmnPJVOHeO2"

# 1. Create session
session_id = create_session(user_id)
print(f"🆕 New session created: {session_id}")

# 2. Save messages
save_message(user_id, session_id, "user", "Hello, I'm feeling stressed today.")
save_message(user_id, session_id, "bot", "I'm here to help. Would you like to talk about it?")

print("💾 Messages saved.")

# 3. Load history
history = load_session_history(user_id, session_id)
print("\n📜 Conversation history:")
for msg in history:
    print(f"[{msg['sender']}] {msg['content']} ({msg['timestamp']})")
