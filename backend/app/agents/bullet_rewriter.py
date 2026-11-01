"""
backend/app/agents/bullet_rewriter.py
Impact & Action-Verb Rewriter Agent (STAR/XYZ Method).
Uses Groq (primary) → Fallback (deterministic).
"""

from __future__ import annotations

import json
import re
from textwrap import dedent
from typing import Any

from app.core.config import get_settings
from app.models.agent import RewrittenBullet
from app.agents.fallback import fallback_rewrite_bullet

settings = get_settings()

_SYSTEM = dedent("""\
You are an elite resume coach specialising in the Google XYZ formula:
"Accomplished [X] as measured by [Y], by doing [Z]"

Rules:
1. Begin with a powerful past-tense action verb (Engineered, Reduced, Led, etc.)
2. Include a quantifiable metric if not present (estimate with plausible numbers like "~20%" or ">50%")
3. Keep to ONE sentence, ≤20 words
4. Do NOT fabricate specific company names, technologies, or events not in the original
5. Return valid JSON ONLY — no explanation text

JSON format:
{
  "rewritten": "<XYZ rewritten bullet>",
  "action_verb": "<first word>",
  "confidence": 0.0-1.0,
  "method": "XYZ"
}
""")


async def rewrite_bullet(
    bullet: str,
    job_role: str = "",
    job_description: str = "",
    context: str = "",
) -> RewrittenBullet:
    """
    Rewrite a resume bullet using XYZ formula.
    Falls back to deterministic rewriter if API is unavailable.
    """
    if not settings.has_groq:
        return fallback_rewrite_bullet(bullet=bullet, job_role=job_role)

    try:
        from groq import AsyncGroq
        client = AsyncGroq(api_key=settings.groq_api_key)

        user_msg = dedent(f"""\
Job Role: {job_role}
Context: {context}
Job Description (first 300 chars): {job_description[:300]}

Original bullet:
{bullet}

Rewrite using the XYZ formula. Return JSON only.
""")
        resp = await client.chat.completions.create(
            model=settings.agent1_model,
            messages=[
                {"role": "system", "content": _SYSTEM},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.4,
            max_tokens=256,
        )
        raw = resp.choices[0].message.content or "{}"
        data = _parse_json(raw)
        return RewrittenBullet(
            original=bullet,
            rewritten=data.get("rewritten", bullet),
            action_verb=data.get("action_verb", ""),
            confidence=float(data.get("confidence", 0.8)),
            method=data.get("method", "XYZ"),
        )
    except Exception:
        return fallback_rewrite_bullet(bullet=bullet, job_role=job_role)


def _parse_json(text: str) -> dict[str, Any]:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}
