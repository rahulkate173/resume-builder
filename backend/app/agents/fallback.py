"""
backend/app/agents/fallback.py
Deterministic fallback agent implementations.
Used when no LLM API keys are available, ensuring the app works offline.
"""

from __future__ import annotations

import re
from typing import Any

from app.models.agent import (
    ATSAuditResult,
    GeneratedSummary,
    JDAnalysis,
    RewrittenBullet,
)

# High-impact action verbs by category
_ACTION_VERBS = {
    "engineering": ["Architected", "Engineered", "Developed", "Implemented", "Optimised",
                    "Refactored", "Deployed", "Automated", "Integrated", "Designed"],
    "leadership": ["Led", "Managed", "Mentored", "Coordinated", "Directed", "Spearheaded"],
    "analysis": ["Analysed", "Evaluated", "Identified", "Investigated", "Measured"],
    "achievement": ["Reduced", "Increased", "Improved", "Accelerated", "Delivered", "Achieved"],
    "default": ["Developed", "Implemented", "Created", "Built", "Designed"],
}


def fallback_rewrite_bullet(
    bullet: str,
    job_role: str = "",
    **_kwargs: Any,
) -> RewrittenBullet:
    """
    Deterministic bullet rewriter using XYZ formula heuristics.
    No LLM required — applies rule-based transformations.
    """
    stripped = bullet.strip().lstrip("•●-– ")

    # Pick strongest action verb
    verbs = _ACTION_VERBS.get("engineering") if any(
        kw in job_role.lower() for kw in ("engineer", "developer", "software", "tech")
    ) else _ACTION_VERBS["default"]
    first_word = stripped.split()[0] if stripped else "Developed"
    action_verb = first_word if first_word[0].isupper() else verbs[0]

    # Simple XYZ template: try to detect if result is present
    has_metric = bool(re.search(r"\d+\s*%|\d+x|\$[\d,]+|\d+\s+ms|\d+\s+users", stripped))
    if has_metric:
        rewritten = stripped  # already quantified, preserve
    else:
        # Append a placeholder metric hint in brackets
        rewritten = f"{stripped} [add quantifiable metric, e.g. reducing X by N%]"

    return RewrittenBullet(
        original=bullet,
        rewritten=rewritten,
        method="XYZ",
        confidence=0.55 if not has_metric else 0.80,
        action_verb=action_verb,
    )


def fallback_ats_audit(
    latex_source: str = "",
    job_description: str = "",
    **_kwargs: Any,
) -> ATSAuditResult:
    """
    Deterministic ATS auditor based on structural heuristics.
    Checks section presence, keyword overlap, and LaTeX validity markers.
    """
    text = latex_source.lower()
    jd_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", job_description.lower()))

    # Check required sections
    sections = {
        "experience": bool(re.search(r"\\section\{experience\}", text, re.I)),
        "education": bool(re.search(r"\\section\{education\}", text, re.I)),
        "skills": bool(re.search(r"\\section\{.*skill", text, re.I)),
        "projects": bool(re.search(r"\\section\{projects\}", text, re.I)),
    }
    section_scores = {k: 25 if v else 0 for k, v in sections.items()}
    base_score = sum(section_scores.values())

    # Keyword density
    resume_words = set(re.findall(r"\b[a-zA-Z]{4,}\b", text))
    overlap = jd_words & resume_words
    match_ratio = len(overlap) / max(len(jd_words), 1)
    keyword_score = min(int(match_ratio * 100), 25)

    total_score = base_score + keyword_score
    warnings = []
    if not sections["experience"]:
        warnings.append("Missing \\section{Experience} — critical ATS section")
    if not sections["education"]:
        warnings.append("Missing \\section{Education} — critical ATS section")
    if match_ratio < 0.3:
        warnings.append("Low keyword overlap with job description (<30%)")
    if len(latex_source) < 500:
        warnings.append("Resume content seems very short — check template fill")
    if "\\begin{document}" not in latex_source:
        warnings.append("LaTeX \\begin{document} tag missing — compilation will fail")

    missing_kw = list(jd_words - resume_words)[:10]

    return ATSAuditResult(
        score=min(total_score + 25, 100),  # +25 base credibility
        section_scores=section_scores,
        warnings=warnings,
        keyword_density={w: 1 for w in list(overlap)[:20]},
        missing_keywords=missing_kw,
        passed=total_score >= 60,
    )


def fallback_parse_jd(job_description: str, **_kwargs: Any) -> JDAnalysis:
    """
    Deterministic JD parser using keyword matching.
    Extracts hard skills, soft skills, and competencies via regex patterns.
    """
    text = job_description.lower()

    # Common tech hard skills
    _tech = [
        "python", "java", "javascript", "typescript", "react", "node", "django",
        "fastapi", "flask", "sql", "nosql", "mongodb", "postgresql", "redis",
        "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd", "git", "rest",
        "graphql", "microservices", "machine learning", "pytorch", "tensorflow",
        "spark", "kafka", "airflow", "terraform",
    ]
    hard_skills = [s for s in _tech if s in text]

    # Soft skills
    _soft = [
        "communication", "leadership", "teamwork", "problem-solving", "collaboration",
        "mentoring", "agile", "scrum", "cross-functional",
    ]
    soft_skills = [s for s in _soft if s in text]

    # Years of experience
    yr_match = re.search(r"(\d+)\+?\s*years? of experience", text)
    required_years = int(yr_match.group(1)) if yr_match else None

    # Seniority inference
    seniority = "mid"
    if any(w in text for w in ["senior", "staff", "principal", "lead"]):
        seniority = "senior"
    elif any(w in text for w in ["junior", "entry", "graduate", "associate"]):
        seniority = "junior"
    elif any(w in text for w in ["director", "vp ", "executive", "head of"]):
        seniority = "executive"

    return JDAnalysis(
        hard_skills=hard_skills,
        soft_skills=soft_skills,
        core_competencies=hard_skills[:5] + soft_skills[:3],
        required_years=required_years,
        seniority=seniority,
        match_matrix={},
        match_score=0,
        missing_keywords=[],
    )


def fallback_generate_summary(
    job_role: str,
    seniority: str = "mid",
    profile_snapshot: dict | None = None,
    **_kwargs: Any,
) -> GeneratedSummary:
    """Deterministic template-based summary generator."""
    snap = profile_snapshot or {}
    name = snap.get("full_name", "").split()[0] or "The candidate"
    exp = snap.get("experience", [])
    exp_text = f" with {len(exp)}+ years of hands-on experience" if exp else ""
    skills = snap.get("skills", [])
    skills_text = (", ".join(skills[:4]) + ", and more") if skills else "a broad technical skill set"

    level_map = {
        "junior": "driven and detail-oriented professional",
        "mid": "results-driven professional",
        "senior": "seasoned engineering leader",
        "executive": "executive-level technology leader",
    }
    level_desc = level_map.get(seniority, "results-driven professional")

    summary = (
        f"{name} is a {level_desc} with expertise in {skills_text}{exp_text}. "
        f"Passionate about building scalable, high-quality solutions for {job_role} roles "
        f"and driving measurable business impact through technical excellence."
    )
    return GeneratedSummary(
        summary=summary,
        seniority=seniority,
        tailored_for=job_role,
    )
