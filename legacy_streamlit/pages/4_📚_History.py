"""
pages/4_📚_History.py
Resume generation history — browse, download, and view past resumes.
"""

from __future__ import annotations

import streamlit as st

from utils.ui_helpers import inject_global_css, page_header, score_badge
from auth.auth import require_auth
from agents.pipeline import get_history, get_history_pdf

st.set_page_config(
    page_title="History — AI Resume Builder",
    page_icon="📚",
    layout="wide",
)
inject_global_css()

user = require_auth()
user_id = user["sub"]

page_header("Resume History", "All your previously generated resumes.", "📚")

history = get_history(user_id, limit=30)

if not history:
    st.markdown(
        """
<div class="rb-card" style="text-align:center;padding:60px 40px;">
  <div style="font-size:4rem;margin-bottom:16px;">📭</div>
  <h3 style="color:#e2e8f0;margin:0 0 8px 0;">No Resumes Yet</h3>
  <p style="color:#94a3b8;margin:0;">Generate your first resume from the <b>Generate Resume</b> page.</p>
</div>
""",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        f"<p style='color:#94a3b8;margin-bottom:16px;'>Showing {len(history)} recent resume(s).</p>",
        unsafe_allow_html=True,
    )

    for entry in history:
        created_at = entry.get("created_at", "")
        if hasattr(created_at, "strftime"):
            created_str = created_at.strftime("%b %d, %Y %H:%M")
        else:
            created_str = str(created_at)[:16]

        score = entry.get("verification_score", 0)
        verified = entry.get("verified", False)
        entry_id = entry.get("_id", "")

        with st.expander(
            f"{'✅' if verified else '⚠️'}  **{entry.get('job_role','?')}** @ {entry.get('company','?')}  —  {created_str}",
            expanded=False,
        ):
            c1, c2, c3, c4 = st.columns([3, 2, 2, 2])
            c1.markdown(f"**Template:** `{entry.get('template_used', 'N/A')}`")
            c2.markdown(f"**Iterations:** {entry.get('agent1_iterations', 0)}")
            c3.markdown(
                f"**Score:** {score_badge(score)}",
                unsafe_allow_html=True,
            )
            c4.markdown(
                f"**PDF:** {'✅ Available' if entry.get('pdf_base64') else '❌ Not available'}"
            )

            if entry.get("verification_notes"):
                st.caption(f"Agent 2 Notes: {entry['verification_notes'][:200]}")

            btn_col1, btn_col2, btn_col3 = st.columns([2, 2, 4])

            # Download LaTeX
            if entry.get("latex_output"):
                btn_col1.download_button(
                    "📄 LaTeX",
                    data=entry["latex_output"],
                    file_name=f"resume_{entry_id}.tex",
                    mime="text/plain",
                    key=f"dl_latex_{entry_id}",
                )

            # Download PDF (loads on demand)
            if btn_col2.button("⬇️ PDF", key=f"load_pdf_{entry_id}"):
                with st.spinner("Loading PDF..."):
                    pdf_bytes = get_history_pdf(entry_id)
                if pdf_bytes:
                    st.download_button(
                        "⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=f"resume_{entry_id}.pdf",
                        mime="application/pdf",
                        key=f"dl_pdf_{entry_id}",
                    )
                else:
                    st.error("PDF not available for this entry.")

            # View LaTeX inline
            if entry.get("latex_output"):
                with st.expander("View LaTeX Source", expanded=False):
                    st.code(entry["latex_output"], language="latex", line_numbers=True)
