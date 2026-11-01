"""
utils/ui_helpers.py
Shared Streamlit UI utilities and styling.
"""

from __future__ import annotations
import streamlit as st


# ── Global CSS ────────────────────────────────────────────────────────────────

def inject_global_css() -> None:
    st.markdown(
        """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

/* ── Dark Background ── */
.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1526 40%, #0a1020 100%) !important;
    min-height: 100vh;
}

/* ── Main container ── */
.block-container {
    padding-top: 1.5rem !important;
    max-width: 1100px !important;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1829 0%, #111d30 100%) !important;
    border-right: 1px solid rgba(99, 179, 237, 0.1) !important;
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }

/* ── Cards ── */
.rb-card {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 16px;
    padding: 24px 28px;
    margin-bottom: 20px;
    backdrop-filter: blur(12px);
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    transition: border-color 0.2s;
}
.rb-card:hover { border-color: rgba(99,179,237,0.35); }

/* ── Gradient headings ── */
.rb-gradient-title {
    background: linear-gradient(135deg, #63b3ed, #9f7aea, #ed64a6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 800;
    letter-spacing: -0.5px;
}

/* ── Metric badges ── */
.rb-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.3px;
}
.rb-badge-green  { background: rgba(72,187,120,0.15); color: #68d391; border: 1px solid rgba(72,187,120,0.3); }
.rb-badge-blue   { background: rgba(99,179,237,0.15); color: #63b3ed; border: 1px solid rgba(99,179,237,0.3); }
.rb-badge-purple { background: rgba(159,122,234,0.15); color: #9f7aea; border: 1px solid rgba(159,122,234,0.3); }
.rb-badge-red    { background: rgba(252,129,129,0.15); color: #fc8181; border: 1px solid rgba(252,129,129,0.3); }

/* ── Streamlit buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #2b6cb0, #6b46c1) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.4rem !important;
    font-weight: 600 !important;
    font-family: 'Inter', sans-serif !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 12px rgba(107, 70, 193, 0.3) !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(107, 70, 193, 0.45) !important;
}

/* ── Input fields ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div {
    background: rgba(15, 23, 42, 0.9) !important;
    border: 1px solid rgba(99, 179, 237, 0.25) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #63b3ed !important;
    box-shadow: 0 0 0 2px rgba(99,179,237,0.2) !important;
}

/* ── Labels ── */
label, .stTextInput label, .stTextArea label, .stSelectbox label {
    color: #94a3b8 !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #63b3ed, #9f7aea) !important;
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0a0e1a; }
::-webkit-scrollbar-thumb { background: #2d3748; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #4a5568; }

/* ── Code blocks ── */
.stCodeBlock { border-radius: 10px !important; }

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: rgba(15,23,42,0.6) !important;
    border-radius: 10px !important;
    padding: 4px !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px !important;
    color: #94a3b8 !important;
}
.stTabs [aria-selected="true"] {
    background: rgba(99,179,237,0.2) !important;
    color: #63b3ed !important;
}

/* ── Divider ── */
hr { border-color: rgba(99,179,237,0.1) !important; }

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
</style>
""",
        unsafe_allow_html=True,
    )


def page_header(title: str, subtitle: str = "", icon: str = "") -> None:
    """Render a styled page header."""
    st.markdown(
        f"""
<div style="margin-bottom:24px;">
  <h1 class="rb-gradient-title" style="font-size:2.2rem;margin:0 0 6px 0;">
    {icon + " " if icon else ""}{title}
  </h1>
  {"<p style='color:#94a3b8;margin:0;font-size:1rem;'>" + subtitle + "</p>" if subtitle else ""}
</div>
""",
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, delta: str = "", color: str = "blue") -> None:
    st.markdown(
        f"""
<div class="rb-card" style="text-align:center;padding:16px;">
  <div style="color:#94a3b8;font-size:0.8rem;font-weight:500;margin-bottom:4px;">{label}</div>
  <div style="font-size:1.6rem;font-weight:700;color:#e2e8f0;">{value}</div>
  {"<div style='font-size:0.75rem;color:#68d391;margin-top:2px;'>" + delta + "</div>" if delta else ""}
</div>
""",
        unsafe_allow_html=True,
    )


def score_badge(score: int) -> str:
    if score >= 80:
        cls = "rb-badge-green"
        label = "Excellent"
    elif score >= 60:
        cls = "rb-badge-blue"
        label = "Good"
    elif score >= 40:
        cls = "rb-badge-purple"
        label = "Fair"
    else:
        cls = "rb-badge-red"
        label = "Needs Work"
    return f'<span class="rb-badge {cls}">{score}/100 — {label}</span>'


def card(content_html: str, extra_style: str = "") -> None:
    st.markdown(
        f'<div class="rb-card" style="{extra_style}">{content_html}</div>',
        unsafe_allow_html=True,
    )
