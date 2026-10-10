"""
pages/2_👤_Profile.py
Internal Details page — stored once at login, editable anytime.
Contains: name, contact, social links, experience, education, projects, skills, etc.
"""

from __future__ import annotations

import streamlit as st
from utils.ui_helpers import inject_global_css, page_header, card
from auth.auth import require_auth, get_profile, save_profile

st.set_page_config(
    page_title="My Profile — AI Resume Builder",
    page_icon="👤",
    layout="wide",
)
inject_global_css()

user = require_auth()
user_id = user["sub"]
username = user["username"]

page_header("My Profile", "Your internal details — stored once, used every time.", "👤")

# Load existing profile
profile = get_profile(user_id)

# ── Helper to manage list sections ───────────────────────────────────────────

def list_editor(key: str, items: list[dict], fields: list[dict]) -> list[dict]:
    """Generic list editor for experience, education, projects, etc."""
    edited = []
    for i, item in enumerate(items):
        with st.expander(f"Entry {i+1} — {item.get(fields[0]['key'], 'New')}", expanded=False):
            row = {}
            cols = st.columns(2)
            for j, field in enumerate(fields):
                col = cols[j % 2]
                if field["type"] == "text":
                    row[field["key"]] = col.text_input(
                        field["label"],
                        value=item.get(field["key"], ""),
                        key=f"{key}_{i}_{field['key']}",
                    )
                elif field["type"] == "textarea":
                    row[field["key"]] = st.text_area(
                        field["label"],
                        value="\n".join(item.get(field["key"], [])) if isinstance(item.get(field["key"]), list) else item.get(field["key"], ""),
                        key=f"{key}_{i}_{field['key']}",
                        height=100,
                    )
                    if isinstance(item.get(field["key"]), list):
                        # Convert back to list
                        row[field["key"]] = [b.strip() for b in row[field["key"]].split("\n") if b.strip()]
            col_del, _ = st.columns([1, 5])
            if col_del.button("🗑 Remove", key=f"del_{key}_{i}"):
                continue   # skip adding this entry
            edited.append(row)
    return edited


# ══ TABS ════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏠 Personal", "💼 Experience", "🎓 Education", "🚀 Projects", "🛠 Skills & More"
])

# ── Tab 1: Personal Info ──────────────────────────────────────────────────────
with tab1:
    st.markdown('<div class="rb-card">', unsafe_allow_html=True)
    st.markdown("#### Personal Information")
    c1, c2 = st.columns(2)
    full_name  = c1.text_input("Full Name *", value=profile.get("full_name", ""))
    email      = c2.text_input("Email *", value=profile.get("email", ""))
    phone      = c1.text_input("Phone", value=profile.get("phone", ""), placeholder="+1-555-0100")
    location   = c2.text_input("Location", value=profile.get("location", ""), placeholder="San Francisco, CA")
    st.markdown("#### Online Presence")
    c3, c4 = st.columns(2)
    linkedin   = c3.text_input("LinkedIn URL", value=profile.get("linkedin", ""), placeholder="https://linkedin.com/in/...")
    github     = c4.text_input("GitHub URL", value=profile.get("github", ""), placeholder="https://github.com/...")
    leetcode   = c3.text_input("LeetCode URL", value=profile.get("leetcode", ""), placeholder="https://leetcode.com/u/...")
    codeforces = c4.text_input("Codeforces URL", value=profile.get("codeforces", ""), placeholder="https://codeforces.com/profile/...")
    portfolio  = c3.text_input("Portfolio / Website", value=profile.get("portfolio", ""))
    kaggle     = c4.text_input("Kaggle URL", value=profile.get("kaggle", ""))
    twitter    = c3.text_input("Twitter / X URL", value=profile.get("twitter", ""))
    st.markdown("#### Professional Summary (optional)")
    professional_summary = st.text_area(
        "Summary / Objective",
        value=profile.get("professional_summary", ""),
        height=100,
        placeholder="3-4 sentences describing your professional identity...",
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ── Tab 2: Experience ─────────────────────────────────────────────────────────
with tab2:
    st.markdown('<div class="rb-card">', unsafe_allow_html=True)
    st.markdown("#### Work Experience")
    st.caption("Add each job. Bullets should be one per line (use • or just press Enter).")

    if "exp_list" not in st.session_state:
        st.session_state["exp_list"] = profile.get("experience", [{}])
    if not st.session_state["exp_list"]:
        st.session_state["exp_list"] = [{}]

    exp_entries = []
    for i, exp in enumerate(st.session_state["exp_list"]):
        with st.expander(f"Experience {i+1} — {exp.get('company', 'New Entry')}", expanded=i == 0):
            c1, c2 = st.columns(2)
            company  = c1.text_input("Company *", value=exp.get("company", ""), key=f"exp_company_{i}")
            role     = c2.text_input("Role / Title *", value=exp.get("role", ""), key=f"exp_role_{i}")
            duration = c1.text_input("Duration", value=exp.get("duration", ""), placeholder="Jan 2022 – Dec 2023", key=f"exp_dur_{i}")
            loc_exp  = c2.text_input("Location", value=exp.get("location", ""), key=f"exp_loc_{i}")
            raw_bullets = "\n".join(exp.get("bullets", []))
            bullets_text = st.text_area("Bullet Points (one per line)", value=raw_bullets, height=120, key=f"exp_bullets_{i}")
            bullets = [b.lstrip("•● ").strip() for b in bullets_text.split("\n") if b.strip()]
            col_remove, _ = st.columns([1, 6])
            if not col_remove.button("🗑 Remove", key=f"rem_exp_{i}"):
                exp_entries.append({
                    "company": company, "role": role,
                    "duration": duration, "location": loc_exp,
                    "bullets": bullets,
                })
    if st.button("➕ Add Experience", key="add_exp"):
        st.session_state["exp_list"].append({})
        st.rerun()
    st.session_state["exp_list"] = exp_entries
    st.markdown('</div>', unsafe_allow_html=True)

# ── Tab 3: Education ──────────────────────────────────────────────────────────
with tab3:
    st.markdown('<div class="rb-card">', unsafe_allow_html=True)
    st.markdown("#### Education")

    if "edu_list" not in st.session_state:
        st.session_state["edu_list"] = profile.get("education", [{}])
    if not st.session_state["edu_list"]:
        st.session_state["edu_list"] = [{}]

    edu_entries = []
    for i, edu in enumerate(st.session_state["edu_list"]):
        with st.expander(f"Education {i+1} — {edu.get('institution', 'New Entry')}", expanded=i == 0):
            c1, c2 = st.columns(2)
            institution = c1.text_input("Institution *", value=edu.get("institution", ""), key=f"edu_inst_{i}")
            degree      = c2.text_input("Degree", value=edu.get("degree", ""), placeholder="B.S. / M.S. / Ph.D.", key=f"edu_deg_{i}")
            field       = c1.text_input("Field of Study", value=edu.get("field", ""), key=f"edu_field_{i}")
            gpa         = c2.text_input("GPA (optional)", value=edu.get("gpa", ""), key=f"edu_gpa_{i}")
            duration    = c1.text_input("Duration", value=edu.get("duration", ""), placeholder="Aug 2018 – May 2022", key=f"edu_dur_{i}")
            raw_b = "\n".join(edu.get("bullets", []))
            bullets_t = st.text_area("Notable courses / achievements (one per line)", value=raw_b, height=80, key=f"edu_b_{i}")
            bullets   = [b.strip() for b in bullets_t.split("\n") if b.strip()]
            col_remove2, _ = st.columns([1, 6])
            if not col_remove2.button("🗑 Remove", key=f"rem_edu_{i}"):
                edu_entries.append({
                    "institution": institution, "degree": degree,
                    "field": field, "gpa": gpa,
                    "duration": duration, "bullets": bullets,
                })
    if st.button("➕ Add Education", key="add_edu"):
        st.session_state["edu_list"].append({})
        st.rerun()
    st.session_state["edu_list"] = edu_entries
    st.markdown('</div>', unsafe_allow_html=True)

# ── Tab 4: Projects ───────────────────────────────────────────────────────────
with tab4:
    st.markdown('<div class="rb-card">', unsafe_allow_html=True)
    st.markdown("#### Projects")

    if "proj_list" not in st.session_state:
        st.session_state["proj_list"] = profile.get("projects", [{}])
    if not st.session_state["proj_list"]:
        st.session_state["proj_list"] = [{}]

    proj_entries = []
    for i, proj in enumerate(st.session_state["proj_list"]):
        with st.expander(f"Project {i+1} — {proj.get('name', 'New Entry')}", expanded=i == 0):
            c1, c2 = st.columns(2)
            name       = c1.text_input("Project Name *", value=proj.get("name", ""), key=f"proj_name_{i}")
            tech_stack = c2.text_input("Tech Stack", value=proj.get("tech_stack", ""), placeholder="Python, FastAPI, React", key=f"proj_tech_{i}")
            duration   = c1.text_input("Duration", value=proj.get("duration", ""), key=f"proj_dur_{i}")
            link       = c2.text_input("Link (GitHub / Live)", value=proj.get("link", ""), key=f"proj_link_{i}")
            raw_b = "\n".join(proj.get("bullets", []))
            bullets_t = st.text_area("Description Bullets (one per line)", value=raw_b, height=100, key=f"proj_b_{i}")
            bullets   = [b.strip() for b in bullets_t.split("\n") if b.strip()]
            col_remove3, _ = st.columns([1, 6])
            if not col_remove3.button("🗑 Remove", key=f"rem_proj_{i}"):
                proj_entries.append({
                    "name": name, "tech_stack": tech_stack,
                    "duration": duration, "link": link, "bullets": bullets,
                })
    if st.button("➕ Add Project", key="add_proj"):
        st.session_state["proj_list"].append({})
        st.rerun()
    st.session_state["proj_list"] = proj_entries
    st.markdown('</div>', unsafe_allow_html=True)

# ── Tab 5: Skills & More ──────────────────────────────────────────────────────
with tab5:
    st.markdown('<div class="rb-card">', unsafe_allow_html=True)
    st.markdown("#### Skills & Technologies")
    skills_raw = st.text_area(
        "Technical Skills (comma-separated)",
        value=", ".join(profile.get("skills", [])),
        height=80,
        placeholder="Python, TypeScript, PyTorch, Docker, Kubernetes...",
    )
    languages_raw = st.text_area(
        "Programming Languages (comma-separated)",
        value=", ".join(profile.get("languages", [])),
        height=60,
        placeholder="Python, C++, JavaScript, Go...",
    )

    st.markdown("#### Certifications")
    certs_raw = st.text_area(
        "Certifications (one per line: Name | Issuer | Date | Link)",
        value="\n".join(
            f"{c.get('name','')} | {c.get('issuer','')} | {c.get('date','')} | {c.get('link','')}"
            for c in profile.get("certifications", [])
        ),
        height=100,
        placeholder="AWS Solutions Architect | Amazon | 2023 | https://...",
    )

    st.markdown("#### Achievements & Awards")
    achv_raw = st.text_area(
        "Achievements (one per line: Title | Description)",
        value="\n".join(
            f"{a.get('title','')} | {a.get('description','')}"
            for a in profile.get("achievements", [])
        ),
        height=100,
        placeholder="Hackathon 1st Place | Won XYZ Hackathon 2023 with 200+ teams",
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ── Save Button ───────────────────────────────────────────────────────────────
st.divider()
col_save, col_msg = st.columns([2, 5])
if col_save.button("💾 Save Profile", use_container_width=True, type="primary"):
    # Build certifications list
    certs = []
    for line in certs_raw.strip().split("\n"):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 1 and parts[0]:
            certs.append({
                "name": parts[0] if len(parts) > 0 else "",
                "issuer": parts[1] if len(parts) > 1 else "",
                "date": parts[2] if len(parts) > 2 else "",
                "link": parts[3] if len(parts) > 3 else "",
            })
    # Build achievements list
    achvs = []
    for line in achv_raw.strip().split("\n"):
        parts = [p.strip() for p in line.split("|")]
        if len(parts) >= 1 and parts[0]:
            achvs.append({
                "title": parts[0],
                "description": parts[1] if len(parts) > 1 else "",
            })

    data = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "location": location,
        "linkedin": linkedin,
        "github": github,
        "leetcode": leetcode,
        "codeforces": codeforces,
        "portfolio": portfolio,
        "kaggle": kaggle,
        "twitter": twitter,
        "professional_summary": professional_summary,
        "experience": st.session_state.get("exp_list", []),
        "education": st.session_state.get("edu_list", []),
        "projects": st.session_state.get("proj_list", []),
        "certifications": certs,
        "achievements": achvs,
        "skills": [s.strip() for s in skills_raw.split(",") if s.strip()],
        "languages": [l.strip() for l in languages_raw.split(",") if l.strip()],
    }
    if save_profile(user_id, data):
        col_msg.success("✅ Profile saved successfully!")
        # Clear cached session lists so they reload fresh
        for k in ["exp_list", "edu_list", "proj_list"]:
            st.session_state.pop(k, None)
    else:
        col_msg.error("❌ Failed to save profile. Please try again.")
