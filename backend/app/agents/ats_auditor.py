"""
backend/app/agents/ats_auditor.py
ATS Auditor & Scoring Agent.
Returns structured score (0-100), critical warnings, and 1-click auto-fix suggestions.
"""

from __future__ import annotations

import json
import re
from textwrap import dedent
from typing import Any

from app.core.config import get_settings
from app.models.agent import ATSAuditResult
from app.agents.fallback import fallback_ats_audit

settings = get_settings()

_SYSTEM = dedent("""\
You are an ATS (Applicant Tracking System) expert and resume quality auditor.

Evaluate the provided resume LaTeX source against the job description and return a structured score.

Criteria:
1. Section completeness (Experience, Education, Skills, Projects) — 25 pts
2. Keyword match density with JD — 25 pts
3. Formatting compliance (one-page signals, action verbs, LaTeX validity) — 25 pts
4. Readability & professionalism (no typos, strong verbs, quantifiable bullets) — 25 pts

Return valid JSON ONLY:
{
  "score": 0-100,
  "section_scores": {"experience": 0-25, "education": 0-25, "skills": 0-25, "formatting": 0-25},
  "warnings": ["warning 1", "warning 2"],
  "auto_fixes": [{"issue": "...", "fix": "..."}],
  "keyword_density": {"keyword": count},
  "missing_keywords": ["kw1", "kw2"],
  "passed": true/false
}
""")


async def audit_ats(
    latex_source: str = "",
    job_description: str = "",
) -> ATSAuditResult:
    """ATS audit with LLM primary + deterministic fallback."""
    if not settings.has_groq or len(latex_source) < 100:
        return fallback_ats_audit(latex_source=latex_source, job_description=job_description)

    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=settings.groq_api_key)

        user_msg = dedent(f"""\
Job Description (first 800 chars):
{job_description[:800]}

LaTeX Resume (first 3000 chars):
{latex_source[:3000]}

Perform the ATS audit and return JSON only.
""")
        resp = await client.chat.completions.create(
            model=settings.agent1_model,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.0,
            max_tokens=1024,
        )
        raw = resp.choices[0].message.content or "{}"
        data = _parse_json(raw)

        return ATSAuditResult(
            score=int(data.get("score", 0)),
            section_scores=data.get("section_scores", {}),
            warnings=data.get("warnings", []),
            auto_fixes=data.get("auto_fixes", []),
            keyword_density=data.get("keyword_density", {}),
            missing_keywords=data.get("missing_keywords", []),
            passed=bool(data.get("passed", False)),
        )
    except Exception:
        return fallback_ats_audit(latex_source=latex_source, job_description=job_description)


def _parse_json(text: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}
