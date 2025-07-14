import uuid
from google.cloud.firestore_v1 import SERVER_TIMESTAMP
from firebase_admin import firestore

def get_user_sessions(user_id):
    db = firestore.client()
    sessions_ref = db.collection("users").document(user_id).collection("sessions")
    docs = sessions_ref.order_by("timestamp_created", direction=firestore.Query.DESCENDING).stream()
    return [{**doc.to_dict(), "session_id": doc.id} for doc in docs]

def create_new_session(uid):
    session_id = str(uuid.uuid4())
    session_ref = (
        firestore.client()
        .collection("users")
        .document(uid)
        .collection("sessions")
        .document(session_id)
    )
    session_ref.set({
        "start_time": SERVER_TIMESTAMP,
        "end_time": None,
        "messages": [],
        "main_concerns": [],
        "sentiment_score": 0,
        "emotions": {},
        "summary": "",
        "timestamp_created": SERVER_TIMESTAMP,
    })
    return session_id
