# db/test_login.py

import getpass
from db.login import login_with_email_and_password

# Replace with your Firebase Web API Key
FIREBASE_API_KEY = "AIzaSyBXuUOnclcpCi9sVzVqHFfOtp6qyC6jlbY"

def main():
    email = input("📧 Email: ")
    password = getpass.getpass("🔑 Password: ")  # Hides input
    uid = login_with_email_and_password(email, password, FIREBASE_API_KEY)
    
    if uid:
        print(f"✅ You can now use UID: {uid} to store/retrieve messages.")
    else:
        print("❌ Try again.")

if __name__ == "__main__":
    main()
