"""
agents/agent1_generator.py
Agent 1 — Resume Generator
Model: Grok / Qwen (via Groq API)

Responsibilities:
 - Selects the best template given the job role
 - Generates tailored, ATS-optimised LaTeX content
 - Loops up to MAX_ITER times if Agent 2 rejects the output
"""

from __future__ import annotations

import json
import re
from textwrap import dedent
from typing import Any

from groq import Groq

from config.settings import get_settings

settings = get_settings()

MAX_ITER = 3  # max self-correction rounds


# ── System prompt ─────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = dedent("""\
You are an expert LaTeX resume writer specialising in ATS-optimised, one-page resumes.

Your job:
1. Analyse the job description, job role, and candidate profile.
2. Select the most appropriate LaTeX template skeleton provided.
3. Fill the template placeholders with tailored, impactful content.
4. Ensure the ENTIRE resume fits on ONE page.
5. Use strong action verbs and quantifiable achievements.
6. Match keywords from the job description.
7. Output ONLY valid, compilable LaTeX — no markdown fences, no explanation.

Rules:
- Do NOT hallucinate experience or skills not present in the profile.
- You MAY reorganise / reword bullet points to better match the JD.
- Keep LaTeX special characters properly escaped (%, &, $, #, _, ^, {, }).
- Competitive programming profiles (LeetCode/Codeforces) should appear in a 
  "Competitive Programming" section when relevant to the role.
""")


def _build_user_prompt(
    job_role: str,
    company: str,
    job_description: str,
    profile: dict[str, Any],
    template_key: str,
    template_latex: str,
    feedback: str = "",
) -> str:
    profile_json = json.dumps(profile, indent=2, default=str)
    feedback_block = f"\n\n## Previous Attempt Feedback\n{feedback}" if feedback else ""
    return dedent(f"""\
## Target Role
Job Role: {job_role}
Company: {company}

## Job Description
{job_description}

## Candidate Profile (JSON)
{profile_json}

## Template: {template_key}
Use the following LaTeX skeleton. Fill ALL {{PLACEHOLDER}} tokens.
{template_latex}
{feedback_block}

## Output
Return ONLY the complete, compilable LaTeX source code.
""")


# ── Main agent function ───────────────────────────────────────────────────────

def run_agent1(
    job_role: str,
    company: str,
    job_description: str,
    profile: dict[str, Any],
    template_key: str,
    template_latex: str,
    feedback: str = "",
    iteration: int = 0,
) -> str:
    """
    Call Agent 1 to generate LaTeX resume content.
    Returns the raw LaTeX string.
    """
    client = Groq(api_key=settings.groq_api_key)

    user_prompt = _build_user_prompt(
        job_role=job_role,
        company=company,
        job_description=job_description,
        profile=profile,
        template_key=template_key,
        template_latex=template_latex,
        feedback=feedback,
    )

    response = client.chat.completions.create(
        model=settings.agent1_model,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=4096,
    )

    raw = response.choices[0].message.content or ""
    # Strip markdown code fences if the model wrapped output
    latex = _strip_fences(raw)
    return latex


# ── Template selector ─────────────────────────────────────────────────────────

def select_template(
    job_role: str,
    job_description: str,
    available_templates: list[str],
) -> str:
    """
    Ask Agent 1 to pick the best template for the given role.
    Returns the template key (e.g. "classic", "modern", "minimal").
    """
    client = Groq(api_key=settings.groq_api_key)

    prompt = dedent(f"""\
You are a resume design expert.

Given the job role and description, choose the most suitable resume template.

Job Role: {job_role}
Job Description (first 500 chars): {job_description[:500]}

Available templates: {', '.join(available_templates)}

Template guidelines:
- "classic"  → academic, research, formal corporate roles
- "modern"   → tech / engineering / product roles
- "minimal"  → ATS-priority, any role where brevity is key

Reply with ONLY the template key — nothing else.
""")

    response = client.chat.completions.create(
        model=settings.agent1_model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,
        max_tokens=10,
    )
    key = (response.choices[0].message.content or "modern").strip().lower()
    return key if key in available_templates else available_templates[0]


# ── Utilities ─────────────────────────────────────────────────────────────────

def _strip_fences(text: str) -> str:
    """Remove ```latex ... ``` or ``` ... ``` fences."""
    text = text.strip()
    text = re.sub(r"^```(?:latex)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()
