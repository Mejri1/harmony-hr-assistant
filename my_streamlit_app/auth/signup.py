import streamlit as st
import time
from auth.auth_service import firebase_signup

def signup_page():
    st.title("🔐 Sign Up")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    if st.button("Sign Up"):
        if not email or not password:
            st.error("Email and password required")
        elif password != confirm_password:
            st.error("Passwords do not match")
        elif len(password) < 6:
            st.error("Password must be at least 6 characters")
        else:
            success, msg = firebase_signup(email, password)
            if success:
                st.success(msg)
                st.info("Redirecting to login...")
                time.sleep(1)
                st.session_state["page"] = "Login"
                st.rerun()
            else:
                st.error(f"Signup failed: {msg}")
