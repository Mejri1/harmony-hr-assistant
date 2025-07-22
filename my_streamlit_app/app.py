import streamlit as st
import time
from datetime import datetime
import sys
import os
import threading
# Project root path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.append(project_root)
from chatbot.memory import get_incremental_summary
from db.firebase import save_session_summary
from firebase_admin import firestore

st.set_page_config(
    page_title="Harmony HR Assistant", 
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from auth.login import login_page
from auth.signup import signup_page
from services.database_service import create_new_session, get_user_sessions
from pages.chatbot_page import chatbot_page as chatbot_ui

def add_custom_css():
    """Add modern CSS styling"""
    st.markdown("""
<style>
    /* Minimalist HR Assistant CSS */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

/* Reset and base styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background-color: #fafafa;
    color: #2c3e50;
    line-height: 1.6;
}

/* Hide Streamlit elements */
#MainMenu, footer, .stDeployButton, header {
    visibility: hidden;
}

/* Main container */
.main-container {
    max-width: 1100px;
    margin: 0 auto;
    padding: 20px;
}

/* Header */
.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    margin-bottom: 30px;
    border-bottom: 1px solid #e8e8e8;
}

.logo {
    font-size: 18px;
    font-weight: 600;
    color: #2c3e50;
    display: flex;
    align-items: center;
    gap: 8px;
}

.user-info {
    display: flex;
    align-items: center;
    gap: 12px;
    font-size: 14px;
    color: #7f8c8d;
}

.user-avatar {
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background: #3498db;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-weight: 500;
    font-size: 13px;
}

/* Cards */
.card {
    background: white;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid #f0f0f0;
    transition: all 0.2s ease;
}

.card:hover {
    border-color: #e0e0e0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}

.card-title {
    font-size: 16px;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 6px;
}

.card-subtitle {
    font-size: 14px;
    color: #7f8c8d;
    margin-bottom: 12px;
}

.card-content {
    font-size: 14px;
    color: #5a6c7d;
    line-height: 1.5;
}

/* Welcome section */
.welcome-section {
    text-align: center;
    padding: 24px;
    margin-bottom: 30px;
}

.welcome-title {
    font-size: 24px;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 8px;
}

.welcome-subtitle {
    font-size: 15px;
    color: #7f8c8d;
    font-weight: 400;
}

/* Quick actions */
.quick-actions {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
    gap: 16px;
    margin-bottom: 30px;
}

.action-card {
    background: white;
    border: 1px solid #f0f0f0;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    transition: all 0.2s ease;
    cursor: pointer;
    text-decoration: none;
    color: inherit;
}

.action-card:hover {
    border-color: #3498db;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(52, 152, 219, 0.1);
}

.action-icon {
    font-size: 20px;
    margin-bottom: 8px;
}

.action-title {
    font-size: 14px;
    font-weight: 500;
    color: #2c3e50;
    margin-bottom: 4px;
}

.action-description {
    font-size: 12px;
    color: #7f8c8d;
}

/* Buttons */
.btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 8px 16px;
    border-radius: 6px;
    border: none;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    text-decoration: none;
    outline: none;
}

.btn-primary {
    background: #3498db;
    color: white;
}

.btn-primary:hover {
    background: #2980b9;
    transform: translateY(-1px);
}

.btn-secondary {
    background: white;
    color: #5a6c7d;
    border: 1px solid #e8e8e8;
}

.btn-secondary:hover {
    background: #f8f9fa;
    border-color: #d0d0d0;
}

.btn-ghost {
    background: transparent;
    color: #7f8c8d;
    border: 1px solid transparent;
}

.btn-ghost:hover {
    background: #f8f9fa;
    color: #5a6c7d;
}

.btn-small {
    padding: 6px 12px;
    font-size: 13px;
}

/* Session list */
.session-list {
    background: white;
    border-radius: 8px;
    border: 1px solid #f0f0f0;
    overflow: hidden;
}

.session-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 16px;
    border-bottom: 1px solid #f8f9fa;
    transition: background-color 0.2s ease;
}

.session-item:last-child {
    border-bottom: none;
}

.session-item:hover {
    background: #fdfdfd;
}

.session-info {
    flex: 1;
}

.session-title {
    font-size: 14px;
    font-weight: 500;
    color: #2c3e50;
    margin-bottom: 2px;
}

.session-date {
    font-size: 12px;
    color: #7f8c8d;
}

.session-status {
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 12px;
    background: #e8f5e8;
    color: #27ae60;
    font-weight: 500;
    margin-right: 12px;
}

/* Chat interface */
.chat-container {
    background: white;
    border-radius: 8px;
    border: 1px solid #f0f0f0;
    height: 500px;
    display: flex;
    flex-direction: column;
}

.chat-header {
    padding: 16px;
    border-bottom: 1px solid #f0f0f0;
    background: #fdfdfd;
}

.chat-title {
    font-size: 16px;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 4px;
}

.chat-subtitle {
    font-size: 13px;
    color: #7f8c8d;
}

.chat-messages {
    flex: 1;
    padding: 16px;
    overflow-y: auto;
}

.chat-input {
    padding: 16px;
    border-top: 1px solid #f0f0f0;
}

/* Navigation */
.nav-tabs {
    display: flex;
    gap: 2px;
    margin-bottom: 20px;
    background: #f8f9fa;
    padding: 4px;
    border-radius: 8px;
}

.nav-tab {
    flex: 1;
    padding: 8px 12px;
    text-align: center;
    border-radius: 6px;
    background: transparent;
    border: none;
    color: #7f8c8d;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
}

.nav-tab.active {
    background: white;
    color: #2c3e50;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.nav-tab:hover:not(.active) {
    color: #5a6c7d;
}

/* Form styles */
.form-group {
    margin-bottom: 16px;
}

.form-label {
    display: block;
    font-size: 13px;
    font-weight: 500;
    color: #2c3e50;
    margin-bottom: 6px;
}

.form-input {
    width: 100%;
    padding: 10px 12px;
    border: 1px solid #e8e8e8;
    border-radius: 6px;
    font-size: 14px;
    transition: border-color 0.2s ease;
    outline: none;
}

.form-input:focus {
    border-color: #3498db;
}

/* Auth container */
.auth-container {
    max-width: 380px;
    margin: 60px auto;
    padding: 30px;
    background: white;
    border-radius: 12px;
    border: 1px solid #f0f0f0;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}

.auth-header {
    text-align: center;
    margin-bottom: 24px;
}

.auth-title {
    font-size: 20px;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 6px;
}

.auth-subtitle {
    font-size: 14px;
    color: #7f8c8d;
}

/* Alerts */
.alert {
    padding: 12px 14px;
    border-radius: 6px;
    margin-bottom: 16px;
    font-size: 14px;
    border-left: 3px solid;
}

.alert-success {
    background: #f0f9ff;
    color: #0c4a6e;
    border-left-color: #3498db;
}

.alert-error {
    background: #fef2f2;
    color: #991b1b;
    border-left-color: #ef4444;
}

.alert-info {
    background: #f0f9ff;
    color: #1e40af;
    border-left-color: #3b82f6;
}

/* Loading state */
.loading {
    text-align: center;
    padding: 40px;
    color: #7f8c8d;
}

.loading-spinner {
    width: 24px;
    height: 24px;
    border: 2px solid #f0f0f0;
    border-top: 2px solid #3498db;
    border-radius: 50%;
    animation: spin 1s linear infinite;
    margin: 0 auto 12px;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* Stats */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 16px;
    margin-bottom: 20px;
}

.stat-card {
    background: white;
    border: 1px solid #f0f0f0;
    border-radius: 8px;
    padding: 16px;
    text-align: center;
    transition: all 0.2s ease;
}

.stat-card:hover {
    border-color: #e0e0e0;
}

.stat-number {
    font-size: 20px;
    font-weight: 600;
    color: #2c3e50;
    margin-bottom: 4px;
}

.stat-label {
    font-size: 12px;
    color: #7f8c8d;
    font-weight: 500;
}

/* Responsive design */
@media (max-width: 768px) {
    .main-container {
        padding: 16px;
    }
    
    .header {
        flex-direction: column;
        gap: 12px;
        text-align: center;
    }
    
    .quick-actions {
        grid-template-columns: 1fr;
    }
    
    .chat-container {
        height: 400px;
    }
    
    .auth-container {
        margin: 20px auto;
        padding: 20px;
    }
}

/* Smooth scrollbar */
::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: #f8f9fa;
}

::-webkit-scrollbar-thumb {
    background: #d0d0d0;
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: #b0b0b0;
}

/* Focus states */
.btn:focus,
.form-input:focus,
.nav-tab:focus {
    outline: 2px solid #3498db;
    outline-offset: 2px;
}

/* Transitions for smooth interactions */
* {
    transition: color 0.2s ease, background-color 0.2s ease, border-color 0.2s ease;
}
    </style>
    """, unsafe_allow_html=True)

def show_loading_animation():
    """Show an enhanced loading animation"""
    with st.spinner('✨ Loading your experience...'):
        progress_bar = st.progress(0)
        for i in range(100):
            time.sleep(0.005)
            progress_bar.progress(i + 1)
        progress_bar.empty()

def summarize_and_save(uid, session_id):
    try:
        db = firestore.client()

        session_ref = db.collection("users").document(uid).collection("sessions").document(session_id)
        messages_ref = session_ref.collection("messages")
        message_docs = messages_ref.stream()

        messages = [doc.to_dict() for doc in message_docs]
        current_message_count = len(messages)
        print(f"[DEBUG] Current message count: {current_message_count}")

        session_doc = session_ref.get()
        if not session_doc.exists:
            print("[ERROR] Session document not found.")
            return

        session_data = session_doc.to_dict()
        saved_summary_count = session_data.get("summary_message_count", 0)
        print(f"[DEBUG] Saved summary count: {saved_summary_count}")

        if current_message_count > saved_summary_count:
            summary = get_incremental_summary(uid, session_id)
            save_session_summary(uid, session_id, summary, current_message_count)
            print("[DEBUG] Session summary updated and saved.")
        else:
            print("[DEBUG] No new messages, skipping summarization.")
    except Exception as e:
        print(f"[ERROR] Failed to save summary in background: {e}")


def welcome_page():
    add_custom_css()
    
    uid = st.session_state.get("uid")
    user_email = st.session_state.get("email", "User").split("@")[0].title()

    # Main header
    st.markdown(f"""
    <div class="main-header">
        <h1>🤖 Harmony HR Assistant</h1>
        <p>Your intelligent HR companion is ready to help</p>
    </div>
    """, unsafe_allow_html=True)

    # Welcome section
    st.markdown(f"""
    <div class="welcome-card">
        <h2>👋 Welcome back, {user_email}!</h2>
        <p>Ready to continue your HR journey? Let's make work life better together.</p>
    </div>
    """, unsafe_allow_html=True)

    # Load previous sessions
    with st.spinner("📋 Loading your conversations..."):
        sessions = get_user_sessions(uid)

    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

    if sessions:
        st.subheader("💬 Your Recent Conversations")
        
        # Display sessions in a more organized way
        for i, session in enumerate(sessions[:5]):  # Show only recent 5
            session_date = session["start_time"].strftime('%B %d, %Y at %I:%M %p')
            
            st.markdown(f"""
            <div class="session-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: #2D3748;">Session {i+1}</h4>
                        <p style="margin: 0; color: #64748B; font-size: 0.9rem;">{session_date}</p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([8, 2])
            with col2:
                if st.button("Continue →", key=f"continue_{i}", use_container_width=True):
                    show_loading_animation()
                    st.session_state["current_session_id"] = session["session_id"]
                    st.session_state["page"] = "chatbot"
                    st.rerun()

        st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)

        # Action buttons
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start New Conversation", use_container_width=True):
                show_loading_animation()
                session_id = create_new_session(uid)
                st.session_state["current_session_id"] = session_id
                st.session_state["page"] = "chatbot"
                st.rerun()

        # Logout button
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("👋 Logout", use_container_width=True):
                logout_user()

    else:
        st.markdown("""
        <div class="welcome-card">
            <h3>🌟 Let's Get Started!</h3>
            <p>You don't have any conversations yet. Start your first conversation to experience the power of Harmony HR Assistant.</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 Start Your First Conversation", use_container_width=True):
                show_loading_animation()
                session_id = create_new_session(uid)
                st.session_state["current_session_id"] = session_id
                st.session_state["page"] = "chatbot"
                st.rerun()

        # Logout button
        col1, col2, col3 = st.columns([3, 2, 3])
        with col2:
            if st.button("👋 Logout", use_container_width=True):
                logout_user()

def chatbot_page():
    add_custom_css()
    
    uid = st.session_state.get("uid")
    session_id = st.session_state.get("current_session_id")
    user_email = st.session_state.get("email", "User")
    
    if not uid or not session_id:
        st.markdown("""
        <div class="error-message">
            <h3>🚨 Session Information Missing</h3>
            <p>Let's get you back on track!</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🏠 Back to Home", key="back_home", use_container_width=True):
                # Summarize and save before going home
                uid = st.session_state.get("uid")
                session_id = st.session_state.get("current_session_id")
                if uid and session_id:
                    threading.Thread(target=summarize_and_save, args=(uid, session_id), daemon=True).start()
                st.session_state["page"] = "welcome"
                st.rerun()
        return
    
    # Chat header
    st.markdown(f"""
    <div class="chat-header">
        <div>
            <h1 style="margin: 0; color: #2D3748;">🤖 Harmony HR Assistant</h1>
            <p style="margin: 0; color: #64748B;">Chatting with {user_email.split('@')[0].title()}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation buttons
    col1, col2, col3 = st.columns([2, 6, 2])
    with col1:
        if st.button("🏠 Home", key="back_to_welcome", use_container_width=True):
            # Summarize and save before going home
            uid = st.session_state.get("uid")
            session_id = st.session_state.get("current_session_id")
            if uid and session_id:
                threading.Thread(target=summarize_and_save, args=(uid, session_id), daemon=True).start()
            st.session_state["page"] = "welcome"
            st.rerun()
    with col3:
        if st.button("👋 Logout", key="logout_chatbot", use_container_width=True):
            logout_user()
    
    try:
        chatbot_ui(uid, session_id)
    except Exception as e:
        st.markdown(f"""
        <div class="error-message">
            <h3>🚨 Something went wrong</h3>
            <p>{str(e)}</p>
            <p>💡 Try refreshing the page or starting a new conversation.</p>
        </div>
        """, unsafe_allow_html=True)

def logout_user():
    """Handle user logout with smooth transition"""
    with st.spinner('👋 Signing you out...'):
        time.sleep(0.5)
    # Summarize and save before logout
    uid = st.session_state.get("uid")
    session_id = st.session_state.get("current_session_id")
    if uid and session_id:
        threading.Thread(target=summarize_and_save, args=(uid, session_id), daemon=True).start()
    for key in ["authenticated", "id_token", "uid", "email", "page", "current_session_id"]:
        if key in st.session_state:
            del st.session_state[key]
    st.markdown("""
    <div class="success-message">
        <h3>✅ Successfully logged out</h3>
        <p>See you soon!</p>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(1)
    st.rerun()

def auth_pages():
    add_custom_css()
    
    
    
    # Initialize auth tab
    if "auth_tab" not in st.session_state:
        st.session_state["auth_tab"] = "login"
    
    # Tab navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔑 Login", key="login_tab", use_container_width=True):
            st.session_state["auth_tab"] = "login"
            st.rerun()
    with col2:
        if st.button("📝 Sign Up", key="signup_tab", use_container_width=True):
            st.session_state["auth_tab"] = "signup"
            st.rerun()
    
    st.markdown('<hr class="custom-divider">', unsafe_allow_html=True)
    
    # Content based on selected tab
    if st.session_state["auth_tab"] == "login":
        st.markdown("""
        <div class="welcome-card">
            <h2>🔑 Welcome Back!</h2>
            <p>Sign in to continue your HR assistance journey</p>
        </div>
        """, unsafe_allow_html=True)
        login_page()
    else:
        st.markdown("""
        <div class="welcome-card">
            <h2>📝 Join Harmony HR!</h2>
            <p>Create your account to get started</p>
        </div>
        """, unsafe_allow_html=True)
        signup_page()

def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "auth"
    
    if st.session_state.get("authenticated"):
        page = st.session_state.get("page", "welcome")
        if page == "welcome":
            welcome_page()
        elif page == "chatbot":
            chatbot_page()
        else:
            welcome_page()
    else:
        auth_pages()

if __name__ == "__main__":
    main()