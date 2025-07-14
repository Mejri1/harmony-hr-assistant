# db/login.py

import requests

def login_with_email_and_password(email: str, password: str, api_key: str):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
    
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        data = response.json()
        print("✅ Login successful!")
        print(f"User ID (UID): {data['localId']}")
        return data['localId']  # This is the user_id you use in Firestore
    else:
        print("❌ Login failed.")
        print("Error:", response.json())
        return None
