"""
backend/app/agents/jd_parser.py
JD Parser & Gap Analysis Agent.
Extracts skills/competencies from a job description and computes match matrix.
"""

from __future__ import annotations

import json
import re
from textwrap import dedent
from typing import Any

from app.core.config import get_settings
from app.models.agent import JDAnalysis
from app.agents.fallback import fallback_parse_jd

settings = get_settings()

_SYSTEM = dedent("""\
You are a job description analyst specialising in talent intelligence.

Given a job description, extract structured data and return valid JSON ONLY:
{
  "hard_skills": ["Python", "Docker", ...],
  "soft_skills": ["Leadership", "Communication", ...],
  "core_competencies": ["System Design", "Agile", ...],
  "required_years": null or integer,
  "seniority": "junior" | "mid" | "senior" | "executive",
  "match_matrix": {},
  "match_score": 0,
  "missing_keywords": []
}

Be comprehensive — extract all explicit AND implied technical requirements.
Return only JSON.
""")


async def parse_jd(
    job_description: str,
    resume_skills: list[str] | None = None,
) -> JDAnalysis:
    """Parse job description. If resume_skills provided, compute gap matrix."""
    if not settings.has_groq:
        result = fallback_parse_jd(job_description)
    else:
        try:
            from groq import AsyncGroq
            client = AsyncGroq(api_key=settings.groq_api_key)

            resp = await client.chat.completions.create(
                model=settings.agent1_model,
                messages=[
                    {"role": "system", "content": _SYSTEM},
                    {"role": "user", "content": f"Job Description:\n{job_description[:2000]}"},
                ],
                temperature=0.1,
                max_tokens=1024,
            )
            raw = resp.choices[0].message.content or "{}"
            data = _parse_json(raw)
            result = JDAnalysis(**data)
        except Exception:
            result = fallback_parse_jd(job_description)

    # Compute match matrix if resume skills provided
    if resume_skills:
        resume_lower = {s.lower() for s in resume_skills}
        all_required = [s.lower() for s in result.hard_skills + result.soft_skills]
        result.match_matrix = {s: (s in resume_lower) for s in all_required}
        matched = sum(result.match_matrix.values())
        result.match_score = int(matched / max(len(all_required), 1) * 100)
        result.missing_keywords = [s for s, present in result.match_matrix.items() if not present]

    return result


def _parse_json(text: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}
