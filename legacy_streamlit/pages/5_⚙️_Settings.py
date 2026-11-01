"""
pages/5_⚙️_Settings.py
Application settings — API keys, model config, LaTeX backend.
"""

import streamlit as st
from utils.ui_helpers import inject_global_css, page_header
from auth.auth import require_auth
from database.connection import ping_db

st.set_page_config(
    page_title="Settings — AI Resume Builder",
    page_icon="⚙️",
    layout="wide",
)
inject_global_css()

user = require_auth()
page_header("Settings", "Configure API keys and model preferences.", "⚙️")

st.markdown(
    """
<div class="rb-card">
  <h4 style="color:#e2e8f0;">🔌 System Status</h4>
</div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
db_ok = ping_db()
c1.metric("MongoDB", "🟢 Connected" if db_ok else "🔴 Disconnected")

from config.settings import get_settings
settings = get_settings()
c2.metric("Agent 1 Model", settings.agent1_model)
c3.metric("LLM 3 Model", settings.llm3_model)

st.divider()

st.markdown(
    """
<div class="rb-card">
<h4 style="color:#e2e8f0;">📋 Configuration</h4>
<p style="color:#94a3b8;font-size:0.9rem;">
Edit your <code>.env</code> file to change settings. A restart is needed after changes.
</p>
</div>
""",
    unsafe_allow_html=True,
)

with st.expander("🔑 Current Config (redacted)"):
    st.json({
        "MONGODB_URI": settings.mongodb_uri.replace(
            settings.mongodb_uri.split("@")[-1] if "@" in settings.mongodb_uri else "", "***"
        ),
        "AGENT1_MODEL": settings.agent1_model,
        "AGENT2_MODEL": settings.agent2_model,
        "LLM3_MODEL": settings.llm3_model,
        "LATEX_BACKEND": settings.latex_backend,
        "LANGSMITH_TRACING": settings.langsmith_tracing,
        "GROQ_API_KEY": "set" if settings.groq_api_key else "NOT SET ⚠️",
        "OPENROUTER_API_KEY": "set" if settings.openrouter_api_key else "NOT SET ⚠️",
        "MISTRALAI_API_KEY": "set" if settings.mistralai_api_key else "NOT SET ⚠️",
    })

st.divider()
st.markdown(
    """
<div class="rb-card">
<h4 style="color:#e2e8f0;">🤖 Agent Architecture</h4>
<pre style="color:#94a3b8;font-size:0.82rem;line-height:1.6;">
Job Role + JD + Company ─┐
Internal Profile ────────┤
Template ────────────────┤
                         ▼
                   [ Agent 1 ]  ← Grok / Qwen (via Groq)
                   Generate tailored LaTeX
                         │
                         ▼  (loop up to 3×)
                   [ Agent 2 ]  ← GPT OSS 120B (via OpenRouter)
                   Verify LaTeX + JD match + experience
                         │ ← feedback → Agent 1
                         │ (passed)
                         ▼
                   Final curated LaTeX  (1 page)
                         │
                         ▼
                   [ LLM 3 ]   ← Mistral Small
                   Final polish
                         │
                         ▼
                   [ MCP Tool ] ← latexonline.cc / pdflatex
                   Compile PDF
                         │
                         ▼
                   ✅ final_resume.pdf
</pre>
</div>
""",
    unsafe_allow_html=True,
)
