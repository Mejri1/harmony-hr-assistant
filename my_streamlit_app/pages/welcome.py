# pages/welcome.py
import streamlit as st
from services.database_service import create_new_session

def welcome_page():
    st.title("👋 Welcome to Harmony HR")
    st.write(f"Hello, {st.session_state.get('email')}!")

    if st.button("Start Conversation"):
        uid = st.session_state.get("uid")
        if not uid:
            st.error("User ID missing. Please login again.")
            return

        session_id = create_new_session(uid)
        st.session_state["session_id"] = session_id
        st.success("✅ Session started!")

        # Navigate to chatbot page (adjust if using multipage differently)
        st.switch_page("pages/chatbot.py")
