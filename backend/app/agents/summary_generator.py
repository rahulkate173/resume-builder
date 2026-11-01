"""
backend/app/agents/summary_generator.py
Executive Summary Synthesizer Agent.
Generates tailored 3-sentence professional summaries.
"""

from __future__ import annotations

import json
import re
from textwrap import dedent
from typing import Any

from app.core.config import get_settings
from app.models.agent import GeneratedSummary
from app.agents.fallback import fallback_generate_summary

settings = get_settings()

_SYSTEM = dedent("""\
You are an elite executive resume writer specialising in compelling professional summaries.

Generate a 3-sentence professional summary following this structure:
1. Who: Seniority level + core identity + years of experience
2. What: Top 2-3 technical strengths tailored to the job role
3. Impact: Career achievement or unique value proposition

Rules:
- No first-person pronouns (no "I", "my", "me")
- Integrate relevant keywords from the job description naturally
- Be specific — avoid vague buzzwords like "passionate" or "enthusiastic"
- Match the seniority level: junior (learning), mid (delivering), senior (leading), executive (transforming)
- Maximum 80 words

Return JSON only:
{
  "summary": "<3-sentence professional summary>",
  "seniority": "<level>",
  "tailored_for": "<job role>"
}
""")


async def generate_summary(
    job_role: str,
    job_description: str = "",
    seniority: str = "mid",
    profile_snapshot: dict[str, Any] | None = None,
) -> GeneratedSummary:
    """Generate executive summary. Falls back to template if no API key."""
    snap = profile_snapshot or {}

    if not settings.has_groq:
        return fallback_generate_summary(
            job_role=job_role,
            seniority=seniority,
            profile_snapshot=snap,
        )

    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=settings.groq_api_key)

        context = dedent(f"""\
Job Role: {job_role}
Seniority: {seniority}
Job Description (first 500 chars): {job_description[:500]}

Candidate Snapshot:
- Name: {snap.get('full_name', '')}
- Skills: {', '.join(snap.get('skills', [])[:10])}
- Languages: {', '.join(snap.get('languages', [])[:6])}
- Years of experience: {len(snap.get('experience', []))} positions
- Education: {snap.get('education', [{}])[0].get('degree', '') if snap.get('education') else 'N/A'}

Generate the 3-sentence summary. Return JSON only.
""")
        resp = await client.chat.completions.create(
            model=settings.agent1_model,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": context},
            ],
            temperature=0.5,
            max_tokens=512,
        )
        raw = resp.choices[0].message.content or "{}"
        data = _parse_json(raw)
        return GeneratedSummary(
            summary=data.get("summary", ""),
            seniority=data.get("seniority", seniority),
            tailored_for=data.get("tailored_for", job_role),
        )
    except Exception:
        return fallback_generate_summary(
            job_role=job_role,
            seniority=seniority,
            profile_snapshot=snap,
        )


def _parse_json(text: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}
