import os
import requests
from firebase_admin import auth
from firebase.firebase_init import db
from dotenv import load_dotenv
from firebase_admin import firestore

load_dotenv()
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

def firebase_signup(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    resp = requests.post(url, json=payload)
    if resp.status_code == 200:
        uid = resp.json()["localId"]
        db.collection("users").document(uid).set({
            "createdAt": firestore.SERVER_TIMESTAMP,
            "email": email,
        })
        db.collection("users").document(uid).collection("global_memory").document("summary").set({
            "summary": "", "topics": [], "keywords": [],
            "sentiment_score": 0, "emotions": {}, "sessions_analyzed": 0,
            "concerns_timeline": [], "timestamp_created": firestore.SERVER_TIMESTAMP,
        })
        return True, "User created successfully"
    return False, resp.json().get("error", {}).get("message", "Signup failed")

def firebase_login(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    resp = requests.post(url, json=payload)
    return (True, resp.json()) if resp.status_code == 200 else (False, resp.json().get("error", {}).get("message", "Login failed"))

def verify_id_token(id_token):
    try:
        return True, auth.verify_id_token(id_token)
    except Exception as e:
        return False, str(e)
