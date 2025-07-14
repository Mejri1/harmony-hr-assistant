import streamlit as st
import time
from datetime import datetime

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
    /* Main app styling */
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
        color: white;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(74, 144, 226, 0.3);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        font-weight: 700;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin: 0;
    }
    
    /* Welcome cards */
    .welcome-card {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1.5rem;
        border-left: 4px solid #4A90E2;
    }
    
    .session-card {
        background: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border: 1px solid #E2E8F0;
        transition: all 0.3s ease;
    }
    
    .session-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 25px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 2px 8px rgba(74, 144, 226, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(74, 144, 226, 0.4);
    }
    
    /* Primary button */
    .primary-button {
        background: linear-gradient(135deg, #4A90E2 0%, #357ABD 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 25px;
        font-weight: 600;
        font-size: 1.1rem;
        box-shadow: 0 4px 15px rgba(74, 144, 226, 0.4);
        transition: all 0.3s ease;
    }
    
    /* Loading animation */
    .loading-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem;
    }
    
    .loading-text {
        font-size: 1.2rem;
        color: #4A90E2;
        font-weight: 600;
    }
    
    /* Stats cards */
    .stats-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-top: 3px solid #4A90E2;
    }
    
    .stats-number {
        font-size: 2rem;
        font-weight: 700;
        color: #4A90E2;
        margin-bottom: 0.5rem;
    }
    
    .stats-label {
        color: #64748B;
        font-weight: 500;
    }
    
    /* Navigation */
    .nav-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
    }
    
    .nav-title {
        font-size: 1.5rem;
        font-weight: 600;
        color: #2D3748;
    }
    
    /* Chat header */
    .chat-header {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    /* Auth container */
    .auth-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 2rem;
    }
    
    .auth-tabs {
        display: flex;
        margin-bottom: 2rem;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Divider */
    .custom-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #4A90E2, transparent);
        margin: 2rem 0;
        border: none;
    }
    
    /* Success/Error messages */
    .success-message {
        background: #D4F6D4;
        color: #2F7D32;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #4CAF50;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #FFE6E6;
        color: #C62828;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #F44336;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
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
    
    st.markdown("""
    <div class="auth-container">
        <div class="main-header">
            <h1>🤖 Harmony HR</h1>
            <p>Your Intelligent HR Assistant</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
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