import streamlit as st
from auth.auth_service import firebase_login, verify_id_token

def login_page():
    st.title("🔑 Login")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if not email or not password:
            st.error("Email and password required")
        else:
            success, result = firebase_login(email, password)
            if success:
                id_token = result["idToken"]
                valid, decoded = verify_id_token(id_token)
                if valid:
                    st.session_state.update({
                        "authenticated": True,
                        "id_token": id_token,
                        "uid": decoded["uid"],
                        "email": email
                    })
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error(f"Token verification failed: {decoded}")
            else:
                st.error(f"Login failed: {result}")
