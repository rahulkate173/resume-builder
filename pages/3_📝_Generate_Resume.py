"""
pages/3_📝_Generate_Resume.py
Main resume generation page.
Takes job role, company, JD every time → runs multi-agent pipeline.
"""

from __future__ import annotations

import time
from datetime import datetime

import streamlit as st

from utils.ui_helpers import inject_global_css, page_header, score_badge, card
from auth.auth import require_auth, get_profile
from agents.pipeline import run_pipeline, PipelineResult
from templates import BUILTIN_TEMPLATES, get_template_names

st.set_page_config(
    page_title="Generate Resume — AI Resume Builder",
    page_icon="📝",
    layout="wide",
)
inject_global_css()

user = require_auth()
user_id = user["sub"]
username = user["username"]

page_header(
    "Generate Resume",
    "Enter the job details below — your AI team will craft a tailored, one-page resume.",
    "📝",
)

# ── Profile check ─────────────────────────────────────────────────────────────
profile = get_profile(user_id)
if not profile.get("full_name"):
    st.warning(
        "⚠️ Your profile is incomplete. Please fill in your [Profile](/Profile) first for best results.",
        icon="⚠️",
    )

# ══ Layout: form on left, live output on right ════════════════════════════════
col_form, col_out = st.columns([5, 6], gap="large")

with col_form:
    st.markdown('<div class="rb-card">', unsafe_allow_html=True)
    st.markdown("#### 🎯 Job Details")
    job_role = st.text_input(
        "Job Role / Title *",
        placeholder="Senior Software Engineer",
        key="gen_job_role",
    )
    company = st.text_input(
        "Company Name *",
        placeholder="Google",
        key="gen_company",
    )
    job_description = st.text_area(
        "Job Description *",
        placeholder="Paste the full job description here...",
        height=260,
        key="gen_jd",
    )
    st.divider()
    st.markdown("#### 🎨 Template")
    template_options = ["auto (AI picks)"] + get_template_names()
    selected_template = st.selectbox(
        "Resume Template",
        options=template_options,
        index=0,
        key="gen_template",
        help="'auto' lets Agent 1 choose the best template for your role.",
    )
    # Template preview cards
    if selected_template != "auto (AI picks)":
        info = BUILTIN_TEMPLATES[selected_template]
        st.markdown(
            f"""<div style="padding:10px;border-radius:8px;border:1px solid rgba(99,179,237,0.2);
            background:rgba(15,23,42,0.5);margin-top:8px;">
            <span style="font-weight:600;color:#63b3ed;">{info['name']}</span>
            <span style="color:#94a3b8;font-size:0.82rem;"> — {info['description']}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    st.divider()
    generate_btn = st.button(
        "🚀 Generate Resume",
        use_container_width=True,
        type="primary",
        key="gen_btn",
        disabled=not (job_role and company and job_description),
    )
    if not (job_role and company and job_description):
        st.caption("Fill in all required fields (*) to enable generation.")
    st.markdown('</div>', unsafe_allow_html=True)

with col_out:
    if "pipeline_result" not in st.session_state:
        st.markdown(
            """
<div class="rb-card" style="text-align:center;padding:60px 40px;">
  <div style="font-size:4rem;margin-bottom:16px;">🤖</div>
  <h3 style="color:#e2e8f0;margin:0 0 8px 0;">Ready to Generate</h3>
  <p style="color:#94a3b8;margin:0;">Fill in the job details and click <b>Generate Resume</b>.</p>
  <p style="color:#64748b;font-size:0.82rem;margin-top:12px;">
    Agent 1 (Grok/Qwen) → Agent 2 Verifier → LLM 3 (Mistral) → PDF
  </p>
</div>
""",
            unsafe_allow_html=True,
        )

# ── Run pipeline ──────────────────────────────────────────────────────────────
if generate_btn and job_role and company and job_description:
    tmpl_key = "auto" if selected_template == "auto (AI picks)" else selected_template

    progress_bar = col_out.progress(0)
    status_text  = col_out.empty()
    log_expander = col_out.expander("📋 Pipeline Log", expanded=False)
    log_lines: list[str] = []

    def update_progress(msg: str, pct: int) -> None:
        progress_bar.progress(pct)
        status_text.markdown(
            f"<p style='color:#94a3b8;font-size:0.9rem;'>{msg}</p>",
            unsafe_allow_html=True,
        )
        log_lines.append(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")
        with log_expander:
            st.markdown("\n".join(f"- {l}" for l in log_lines))

    with col_out:
        start = time.time()
        result: PipelineResult = run_pipeline(
            job_role=job_role,
            company=company,
            job_description=job_description,
            profile=profile,
            user_id=user_id,
            template_key=tmpl_key,
            progress_cb=update_progress,
        )
        elapsed = time.time() - start

    progress_bar.empty()
    status_text.empty()
    st.session_state["pipeline_result"] = result
    st.session_state["gen_elapsed"] = elapsed
    st.rerun()

# ── Display result ────────────────────────────────────────────────────────────
if "pipeline_result" in st.session_state:
    result: PipelineResult = st.session_state["pipeline_result"]
    elapsed = st.session_state.get("gen_elapsed", 0)

    with col_out:
        if result.success:
            # ── Score Header ──────────────────────────────────────────────
            vr = result.verification_result
            score = vr.get("score", 0)
            st.markdown(
                f"""<div class="rb-card" style="padding:16px 20px;margin-bottom:12px;">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
    <div>
      <span style="color:#68d391;font-weight:700;font-size:1.05rem;">✅ Resume Generated!</span>
      <span style="color:#64748b;font-size:0.82rem;margin-left:12px;">in {elapsed:.1f}s · {result.iterations} iteration(s)</span>
    </div>
    {score_badge(score)}
  </div>
  <div style="margin-top:10px;display:flex;gap:16px;flex-wrap:wrap;">
    <span style="color:#94a3b8;font-size:0.82rem;">Template: <b style="color:#63b3ed;">{result.template_key}</b></span>
    <span style="color:#94a3b8;font-size:0.82rem;">JD Match: <b style="color:#9f7aea;">{vr.get('jd_match_score', 0)}/100</b></span>
    <span style="color:#94a3b8;font-size:0.82rem;">Exp. Relevance: <b style="color:#9f7aea;">{vr.get('experience_relevance_score', 0)}/100</b></span>
    <span style="color:#94a3b8;font-size:0.82rem;">PDF: <b style="color:{'#68d391' if result.pdf_success else '#fc8181'};">{'✅ Ready' if result.pdf_success else '⚠️ ' + result.pdf_error[:40]}</b></span>
  </div>
</div>""",
                unsafe_allow_html=True,
            )

            # ── Verifier issues ───────────────────────────────────────────
            if vr.get("issues"):
                with st.expander("⚠️ Verifier Notes", expanded=False):
                    for issue in vr["issues"]:
                        st.markdown(f"- {issue}")
                    if vr.get("feedback"):
                        st.caption(vr["feedback"])

            # ── Output Tabs ───────────────────────────────────────────────
            out_tab1, out_tab2 = st.tabs(["📄 PDF Download", "📝 LaTeX Source"])

            with out_tab1:
                if result.pdf_success and result.pdf_bytes:
                    st.download_button(
                        label="⬇️ Download PDF Resume",
                        data=result.pdf_bytes,
                        file_name=f"resume_{job_role.replace(' ','_').lower()}_{company.replace(' ','_').lower()}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                        type="primary",
                    )
                    st.success("Your one-page resume PDF is ready to download!")
                else:
                    st.warning(
                        f"PDF compilation encountered an issue: {result.pdf_error}\n\n"
                        "You can copy the LaTeX source and compile it manually at "
                        "[Overleaf](https://overleaf.com) or [LaTeX Online](https://latexonline.cc)."
                    )

            with out_tab2:
                st.code(result.final_latex, language="latex", line_numbers=True)
                st.download_button(
                    label="⬇️ Download LaTeX Source",
                    data=result.final_latex,
                    file_name=f"resume_{job_role.replace(' ','_').lower()}.tex",
                    mime="text/plain",
                    use_container_width=True,
                )

        else:
            st.markdown(
                f"""<div class="rb-card">
  <h3 style="color:#fc8181;">❌ Generation Failed</h3>
  <p style="color:#94a3b8;">{result.error}</p>
  <p style="color:#64748b;font-size:0.82rem;">Check your API keys in the <code>.env</code> file and try again.</p>
</div>""",
                unsafe_allow_html=True,
            )

    # ── Clear button ─────────────────────────────────────────────────────────
    if st.button("🔄 Generate Another", key="gen_clear"):
        st.session_state.pop("pipeline_result", None)
        st.session_state.pop("gen_elapsed", None)
        st.rerun()
