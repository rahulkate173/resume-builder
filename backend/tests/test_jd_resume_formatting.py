"""Regression tests for ATS-friendly JD resume formatting."""

from app.agents.jd_resume_pipeline import (
    _deterministic_fill,
    _extract_essential_profile,
)
from app.routers.jd_resume import JDResumeRequest
from app.services.latex_templates import get_template


def test_jd_resume_defaults_to_single_column_ats_template():
    request = JDResumeRequest(
        job_role="Software Engineer",
        company="Example",
        job_description="Build reliable software systems.",
    )

    assert request.template_key == "executive"


def test_resume_profile_keeps_projects_and_limits_page_content():
    profile = {
        "projects": [{"name": "Resume Builder", "bullets": ["Built it"]}],
        "experience": [
            {"company": "Example", "bullets": ["Delivered feature"]},
        ],
        "skills": [f"Skill {index}" for index in range(20)],
    }

    essential = _extract_essential_profile(profile)

    assert essential["projects"] == profile["projects"]
    assert len(essential["skills"]) == 16


def test_deterministic_jd_resume_formats_entries_as_ats_bullets():
    profile = {
        "full_name": "Jane Doe",
        "education": [{
            "institution": "Example University",
            "degree": "B.S.",
            "field": "Computer Science",
            "duration": "2022-2026",
        }],
        "experience": [{
            "company": "Example Co.",
            "role": "Engineer",
            "duration": "2024-Present",
            "bullets": ["Built a reliable service"],
        }],
        "projects": [{
            "name": "Resume Builder",
            "tech_stack": "Python, FastAPI",
            "bullets": ["Created an ATS-friendly resume tool"],
        }],
        "skills": ["Python", "FastAPI"],
    }

    latex = _deterministic_fill(
        get_template("executive"),
        profile,
        "Software Engineer",
        "Example",
    )

    assert "{{" not in latex
    assert "\\resumeSubheading{Example Co.}{2024-Present}{Engineer}" in latex
    assert "\\resumeItemListStart\n  \\resumeItem{Built a reliable service}\n\\resumeItemListEnd" in latex
    assert "\\resumeProjectHeading{\\textbf{Resume Builder} $|$ \\emph{Python, FastAPI}}" in latex
    assert "Created an ATS-friendly resume tool" in latex
