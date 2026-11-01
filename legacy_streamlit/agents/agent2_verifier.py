"""
agents/agent2_verifier.py
Agent 2 — Resume Verifier
Model: GPT OSS 120B class (via OpenRouter — e.g. meta-llama/llama-3.1-405b-instruct)

Responsibilities:
 - Verify the LaTeX is syntactically valid
 - Check JD keyword match and relevance
 - Verify experience alignment
 - Ensure one-page constraint signals are present
 - Return structured pass/fail with detailed feedback
"""

from __future__ import annotations

import json
import re
from textwrap import dedent
from typing import Any

from openai import OpenAI

from config.settings import get_settings

settings = get_settings()

_OPENROUTER_BASE = "https://openrouter.ai/api/v1"

_SYSTEM_PROMPT = dedent("""\
You are a strict resume quality-assurance expert and LaTeX specialist.

Your job is to evaluate a resume LaTeX source against the job description and candidate profile.

Evaluation criteria:
1. LaTeX validity — does the source look compilable? (check \\begin{document}, \\end{document}, balanced braces)
2. JD Match — does the resume highlight keywords and skills from the job description?
3. Experience relevance — are the highlighted experiences relevant to the JD?
4. One-page compliance — are there signs the resume will fit on one page? (limited sections, concise bullets)
5. No fabrication — does the resume only use info present in the profile? (no hallucinated companies, degrees, etc.)
6. Grammar & professionalism — no typos, strong action verbs.

Output a JSON object:
{
  "passed": true/false,
  "score": 0-100,
  "issues": ["issue 1", "issue 2", ...],
  "feedback": "Concise paragraph of specific, actionable feedback for the generator agent.",
  "latex_valid": true/false,
  "jd_match_score": 0-100,
  "experience_relevance_score": 0-100
}

Be strict. Score >= 80 → passed=true. Otherwise passed=false.
""")


def _build_prompt(
    job_role: str,
    company: str,
    job_description: str,
    profile: dict[str, Any],
    latex_source: str,
) -> str:
    profile_json = json.dumps(profile, indent=2, default=str)
    return dedent(f"""\
## Job Role: {job_role} @ {company}

## Job Description
{job_description}

## Candidate Profile
{profile_json}

## Generated LaTeX Resume
```latex
{latex_source}
```

Evaluate and respond with the JSON structure described in your instructions.
""")


def run_agent2(
    job_role: str,
    company: str,
    job_description: str,
    profile: dict[str, Any],
    latex_source: str,
) -> dict[str, Any]:
    """
    Run Agent 2 verifier.
    Returns a dict: {passed, score, issues, feedback, latex_valid,
                     jd_match_score, experience_relevance_score}
    """
    client = OpenAI(
        api_key=settings.openrouter_api_key,
        base_url=_OPENROUTER_BASE,
    )

    user_prompt = _build_prompt(
        job_role=job_role,
        company=company,
        job_description=job_description,
        profile=profile,
        latex_source=latex_source,
    )

    response = client.chat.completions.create(
        model=settings.agent2_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.0,
        max_tokens=1024,
        extra_headers={
            "HTTP-Referer": "https://github.com/resume-builder",
            "X-Title": "AI Resume Builder",
        },
    )

    raw = response.choices[0].message.content or "{}"
    return _parse_verdict(raw)


def _parse_verdict(raw: str) -> dict[str, Any]:
    """Extract JSON from the model's response."""
    # Try to find JSON block
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            data = json.loads(match.group())
            # Normalise keys
            return {
                "passed": bool(data.get("passed", False)),
                "score": int(data.get("score", 0)),
                "issues": list(data.get("issues", [])),
                "feedback": str(data.get("feedback", "")),
                "latex_valid": bool(data.get("latex_valid", True)),
                "jd_match_score": int(data.get("jd_match_score", 0)),
                "experience_relevance_score": int(data.get("experience_relevance_score", 0)),
            }
        except (json.JSONDecodeError, ValueError):
            pass
    # Fallback — treat as failure
    return {
        "passed": False,
        "score": 0,
        "issues": ["Could not parse verifier response."],
        "feedback": raw[:500],
        "latex_valid": False,
        "jd_match_score": 0,
        "experience_relevance_score": 0,
    }
