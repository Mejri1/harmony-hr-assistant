import firebase_admin
from firebase_admin import credentials, firestore
import os

# Path to your Firebase Admin SDK key
SERVICE_ACCOUNT_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "hr-chatbot-e2074-firebase-adminsdk-fbsvc-483a3fba17.json"
)
SERVICE_ACCOUNT_PATH = os.path.abspath(SERVICE_ACCOUNT_PATH)

# Initialize Firebase app once
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)

# Export the Firestore client
db = firestore.client()

def create_session(user_id: str) -> str:
    """Create a new session document for the user and return the session_id."""
    session_ref = db.collection("users").document(user_id).collection("sessions").document()
    session_ref.set({
        "started_at": firestore.SERVER_TIMESTAMP,
        "status": "active"
    })
    return session_ref.id

def load_messages(user_id, session_id):
    messages_ref = db.collection("users") \
        .document(user_id) \
        .collection("sessions") \
        .document(session_id) \
        .collection("messages") \
        .order_by("timestamp")

    docs = messages_ref.stream()
    messages = []
    for doc in docs:
        data = doc.to_dict()
        messages.append({
            "content": data.get("content", ""),
            "sender": data.get("sender", ""),
            "timestamp": data.get("timestamp")
        })
    return messages

def save_message(user_id: str, session_id: str, sender: str, content: str):
    """Save a single message (user or bot) under a session."""
    message_ref = db.collection("users").document(user_id) \
        .collection("sessions").document(session_id) \
        .collection("messages").document()

    message_ref.set({
        "sender": sender,
        "content": content,
        "timestamp": firestore.SERVER_TIMESTAMP
    })

def load_session_history(user_id: str, session_id: str) -> list[dict]:
    """Load all messages from a session, ordered by timestamp."""
    messages_ref = db.collection("users").document(user_id) \
        .collection("sessions").document(session_id) \
        .collection("messages").order_by("timestamp")

    messages = messages_ref.stream()
    history = []
    for msg in messages:
        msg_data = msg.to_dict()
        history.append({
            "sender": msg_data.get("sender"),
            "content": msg_data.get("content"),
            "timestamp": msg_data.get("timestamp")
        })
    return history

def save_session_summary(user_id: str, session_id: str, summary: str):
    """Save the conversation summary to the session document."""
    session_ref = db.collection("users").document(user_id).collection("sessions").document(session_id)
    session_ref.set({"summary": summary}, merge=True)

def load_session_summary(user_id: str, session_id: str) -> str:
    """Load the conversation summary from the session document."""
    session_ref = db.collection("users").document(user_id).collection("sessions").document(session_id)
    doc = session_ref.get()
    if doc.exists:
        return doc.to_dict().get("summary", "")
    return ""

def load_all_session_summaries(user_id: str) -> list:
    sessions_ref = db.collection("users").document(user_id).collection("sessions")
    snapshots = sessions_ref.stream()
    return [doc.to_dict() for doc in snapshots]

def save_global_summary(user_id: str, memory: dict):
    summary_ref = (
        db.collection("users")
        .document(user_id)
        .collection("global_memory")
        .document("summary")
    )
    summary_ref.set(memory, merge=True)