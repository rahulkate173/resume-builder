"""
app.py
Main entry-point for the AI Resume Builder Streamlit application.
Handles navigation, sidebar, and authenticated dashboard.
"""

import streamlit as st
from utils.ui_helpers import inject_global_css, page_header, card
from auth.auth import get_current_user, logout, get_profile
from database.connection import ping_db

st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://github.com/your-org/resume-builder",
        "Report a bug": "https://github.com/your-org/resume-builder/issues",
        "About": "AI Resume Builder — Powered by Grok, GPT OSS 120B & Mistral.",
    },
)

inject_global_css()

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo / brand
    st.markdown(
        """
<div style="padding:16px 0 24px 0;text-align:center;">
  <div style="font-size:2.4rem;">📄</div>
  <div style="font-size:1.1rem;font-weight:700;color:#63b3ed;margin-top:4px;">AI Resume Builder</div>
  <div style="font-size:0.72rem;color:#64748b;margin-top:2px;">v1.0.0 · MIT License</div>
</div>
""",
        unsafe_allow_html=True,
    )

    user = get_current_user()
    if user:
        st.markdown(
            f"""
<div style="background:rgba(99,179,237,0.08);border:1px solid rgba(99,179,237,0.15);
border-radius:10px;padding:12px 14px;margin-bottom:16px;">
  <div style="font-weight:600;color:#e2e8f0;">👋 {user['username']}</div>
  <div style="font-size:0.75rem;color:#64748b;">Logged in</div>
</div>
""",
            unsafe_allow_html=True,
        )
        if st.button("🚪 Logout", use_container_width=True, key="sidebar_logout"):
            logout()
            st.rerun()

    # DB status dot
    db_ok = ping_db()
    st.markdown(
        f"<div style='font-size:0.75rem;color:#{'68d391' if db_ok else 'fc8181'};margin-top:8px;'>"
        f"{'🟢' if db_ok else '🔴'} MongoDB {'Connected' if db_ok else 'Disconnected'}</div>",
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown(
        """
<div style="font-size:0.75rem;color:#475569;line-height:1.6;">
  <b style="color:#64748b;">Agent Stack</b><br>
  🔵 Agent 1 — Groq (Grok/Qwen)<br>
  🟣 Agent 2 — GPT OSS 120B<br>
  🟢 LLM 3 — Mistral Small<br>
  📎 MCP — LaTeX → PDF
</div>
""",
        unsafe_allow_html=True,
    )

# ── Main dashboard ─────────────────────────────────────────────────────────────
user = get_current_user()

if not user:
    # Landing page for unauthenticated users
    page_header(
        "AI Resume Builder",
        "Craft ATS-optimised, one-page resumes powered by a multi-agent AI pipeline.",
        "📄",
    )

    st.markdown(
        """
<div class="rb-card" style="text-align:center;padding:40px 32px;margin-bottom:24px;">
  <h2 style="color:#e2e8f0;margin:0 0 12px 0;">Welcome to AI Resume Builder</h2>
  <p style="color:#94a3b8;max-width:600px;margin:0 auto 24px auto;line-height:1.7;">
    Your personal AI team — <b style="color:#63b3ed;">Agent 1</b> generates,
    <b style="color:#9f7aea;">Agent 2</b> verifies, and
    <b style="color:#68d391;">Mistral</b> polishes your resume into a stunning PDF.
    Enter your details once, generate for any job, any time.
  </p>
  <a href="/Login" target="_self">
    <button style="background:linear-gradient(135deg,#2b6cb0,#6b46c1);color:white;
    border:none;border-radius:10px;padding:12px 32px;font-size:1rem;font-weight:600;
    cursor:pointer;box-shadow:0 4px 20px rgba(107,70,193,0.4);">
      Get Started →
    </button>
  </a>
</div>
""",
        unsafe_allow_html=True,
    )

    # Feature cards
    f1, f2, f3 = st.columns(3)
    with f1:
        st.markdown(
            """<div class="rb-card" style="text-align:center;padding:24px;">
  <div style="font-size:2.5rem;margin-bottom:12px;">🤖</div>
  <h4 style="color:#63b3ed;margin:0 0 8px 0;">Multi-Agent AI</h4>
  <p style="color:#94a3b8;font-size:0.85rem;margin:0;">3-agent pipeline with self-verification loop and feedback cycles.</p>
</div>""",
            unsafe_allow_html=True,
        )
    with f2:
        st.markdown(
            """<div class="rb-card" style="text-align:center;padding:24px;">
  <div style="font-size:2.5rem;margin-bottom:12px;">📎</div>
  <h4 style="color:#9f7aea;margin:0 0 8px 0;">MCP PDF Generation</h4>
  <p style="color:#94a3b8;font-size:0.85rem;margin:0;">LaTeX compiled to pixel-perfect PDF via Model Context Protocol.</p>
</div>""",
            unsafe_allow_html=True,
        )
    with f3:
        st.markdown(
            """<div class="rb-card" style="text-align:center;padding:24px;">
  <div style="font-size:2.5rem;margin-bottom:12px;">🎯</div>
  <h4 style="color:#68d391;margin:0 0 8px 0;">JD-Tailored Output</h4>
  <p style="color:#94a3b8;font-size:0.85rem;margin:0;">Keywords matched, experience curated, ATS-ready — every time.</p>
</div>""",
            unsafe_allow_html=True,
        )

else:
    # Authenticated dashboard
    profile = get_profile(user["sub"])
    name = profile.get("full_name") or user["username"]

    page_header(f"Welcome back, {name.split()[0]}!", "Your AI resume team is ready.", "🏠")

    # Quick stats
    from database.connection import get_db
    db = get_db()
    total_resumes = db.history.count_documents({"user_id": user["sub"]})
    profile_complete = bool(profile.get("full_name") and profile.get("experience"))

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""<div class="rb-card" style="text-align:center;padding:20px;">
  <div style="font-size:2rem;font-weight:800;color:#63b3ed;">{total_resumes}</div>
  <div style="color:#94a3b8;font-size:0.85rem;margin-top:4px;">Resumes Generated</div>
</div>""",
            unsafe_allow_html=True,
        )
    with c2:
        last_doc = db.history.find_one({"user_id": user["sub"]}, sort=[("created_at", -1)])
        last_role = last_doc.get("job_role", "—") if last_doc else "—"
        st.markdown(
            f"""<div class="rb-card" style="text-align:center;padding:20px;">
  <div style="font-size:1.2rem;font-weight:700;color:#9f7aea;">{last_role[:20]}</div>
  <div style="color:#94a3b8;font-size:0.85rem;margin-top:4px;">Last Generated Role</div>
</div>""",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""<div class="rb-card" style="text-align:center;padding:20px;">
  <div style="font-size:1.5rem;">{'✅' if profile_complete else '⚠️'}</div>
  <div style="color:#94a3b8;font-size:0.85rem;margin-top:4px;">Profile {'Complete' if profile_complete else 'Incomplete'}</div>
</div>""",
            unsafe_allow_html=True,
        )

    st.divider()

    # CTA buttons
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if st.button("📝 Generate Resume", use_container_width=True, type="primary"):
            st.switch_page("pages/3_📝_Generate_Resume.py")
    with col_b:
        if st.button("👤 Edit Profile", use_container_width=True):
            st.switch_page("pages/2_👤_Profile.py")
    with col_c:
        if st.button("📚 View History", use_container_width=True):
            st.switch_page("pages/4_📚_History.py")

    if not profile_complete:
        st.info(
            "💡 **Tip:** Complete your [Profile](/Profile) for better resume results. "
            "The more detail you provide, the more tailored your resume will be.",
            icon="💡",
        )
