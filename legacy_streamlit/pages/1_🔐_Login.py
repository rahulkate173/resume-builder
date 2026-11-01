"""
pages/1_🔐_Login.py
Login and Registration page for the AI Resume Builder.
"""

import streamlit as st
from utils.ui_helpers import inject_global_css, page_header
from auth.auth import login_user, register_user, get_current_user

st.set_page_config(
    page_title="Login — AI Resume Builder",
    page_icon="🔐",
    layout="centered",
)
inject_global_css()

# Redirect if already logged in
user = get_current_user()
if user:
    st.switch_page("app.py")

page_header("AI Resume Builder", "Sign in to craft your perfect resume.", "📄")

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_login, tab_register = st.tabs(["🔑 Sign In", "✨ Create Account"])

with tab_login:
    st.markdown('<div class="rb-card">', unsafe_allow_html=True)
    st.markdown("#### Welcome back!")
    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="your_username", key="login_user")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
        submitted = st.form_submit_button("Sign In →", use_container_width=True)

    if submitted:
        if not username or not password:
            st.error("Please fill in all fields.")
        else:
            with st.spinner("Authenticating..."):
                success, msg, token = login_user(username, password)
            if success:
                st.session_state["auth_token"] = token
                st.session_state["username"] = username
                st.success(msg)
                st.balloons()
                st.switch_page("app.py")
            else:
                st.error(msg)
    st.markdown('</div>', unsafe_allow_html=True)

with tab_register:
    st.markdown('<div class="rb-card">', unsafe_allow_html=True)
    st.markdown("#### Create your account")
    st.markdown(
        "<p style='color:#94a3b8;font-size:0.85rem;'>Your profile details are stored once and reused every time.</p>",
        unsafe_allow_html=True,
    )
    with st.form("register_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            new_user = st.text_input("Username *", placeholder="john_doe")
        with col2:
            new_email = st.text_input("Email *", placeholder="john@example.com")
        new_pass = st.text_input("Password *", type="password", placeholder="min 8 characters")
        new_pass2 = st.text_input("Confirm Password *", type="password", placeholder="••••••••")
        reg_submitted = st.form_submit_button("Create Account →", use_container_width=True)

    if reg_submitted:
        if not all([new_user, new_email, new_pass, new_pass2]):
            st.error("All fields are required.")
        elif len(new_pass) < 8:
            st.error("Password must be at least 8 characters.")
        elif new_pass != new_pass2:
            st.error("Passwords do not match.")
        else:
            with st.spinner("Creating account..."):
                success, msg = register_user(new_user, new_email, new_pass)
            if success:
                st.success(f"✅ {msg} Please sign in.")
            else:
                st.error(msg)
    st.markdown('</div>', unsafe_allow_html=True)
