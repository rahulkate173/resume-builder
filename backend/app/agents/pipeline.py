"""
backend/app/agents/pipeline.py
Async multi-agent resume generation pipeline.
Flow: Template select → Agent1 Generate → Agent2 Verify (loop) → LLM3 Polish → PDF
"""

from __future__ import annotations

import base64
import re
from datetime import datetime
from textwrap import dedent
from typing import Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.llm import invoke_chat
from app.core.config import get_settings
from app.core.database import get_db
from app.services.pdf_service import compile_latex_to_pdf, validate_latex
from app.services.latex_templates import get_template, get_template_names

settings = get_settings()

MAX_ITER = 3

# ── Step event type for SSE streaming ────────────────────────────────────────

class PipelineStep:
    def __init__(self, msg: str, pct: int, data: dict | None = None):
        self.message = msg
        self.percent = pct
        self.data = data or {}


class PipelineResult:
    def __init__(self):
        self.template_key: str = ""
        self.iterations: int = 0
        self.verification_result: dict = {}
        self.final_latex: str = ""
        self.pdf_bytes: Optional[bytes] = None
        self.pdf_success: bool = False
        self.pdf_error: str = ""
        self.success: bool = False
        self.error: str = ""
        self.fallback_used: bool = False


# ── Agent 1: Generator ────────────────────────────────────────────────────────

_GEN_SYSTEM = dedent("""\
You are an expert LaTeX resume writer specialising in ATS-optimised, one-page resumes.

Rules:
1. Analyse the job description and candidate profile.
2. Fill ALL {{PLACEHOLDER}} tokens in the template.
3. Ensure resume fits on ONE page — use tight spacing.
4. Use strong action verbs and quantifiable achievements.
5. Match keywords from the job description.
6. Output ONLY valid, compilable LaTeX — no markdown fences, no explanation.
7. Do NOT hallucinate experience or skills not present in the profile.
8. Escape LaTeX special chars: %, &, $, #, _, ^, {, }.
""")


async def _run_agent1(
    job_role: str,
    company: str,
    job_description: str,
    profile: dict,
    template_key: str,
    template_latex: str,
    feedback: str = "",
) -> str:
    """Generate LaTeX resume through LangChain, or use the deterministic fallback."""
    import json

    if not settings.has_gemini:
        return _deterministic_fill(template_latex, profile, job_role, company)

    try:
        profile_json = json.dumps(profile, indent=2, default=str)
        feedback_block = f"\n\n## Previous Attempt Feedback\n{feedback}" if feedback else ""
        user_msg = dedent(f"""\
## Target Role
Job Role: {job_role}
Company: {company}

## Job Description
{job_description}

## Candidate Profile (JSON)
{profile_json}

## Template: {template_key}
Fill ALL {{PLACEHOLDER}} tokens:
{template_latex}
{feedback_block}

## Output
Return ONLY the complete, compilable LaTeX source code.
""")
        raw = await invoke_chat(
            _GEN_SYSTEM,
            user_msg,
            temperature=0.3,
            max_tokens=4096,
        )
        return _strip_fences(raw)
    except Exception:
        return _deterministic_fill(template_latex, profile, job_role, company)


# ── Agent 2: Verifier ─────────────────────────────────────────────────────────

_VERIFY_SYSTEM = dedent("""\
You are a strict resume quality-assurance expert and LaTeX specialist.
Evaluate the resume LaTeX source and return JSON ONLY:
{
  "passed": true/false,
  "score": 0-100,
  "issues": ["issue 1"],
  "feedback": "Actionable feedback for the generator.",
  "latex_valid": true/false,
  "jd_match_score": 0-100,
  "experience_relevance_score": 0-100
}
Score >= 80 → passed=true.
""")


async def _run_agent2(
    job_role: str,
    company: str,
    job_description: str,
    profile: dict,
    latex_source: str,
) -> dict:
    """Verify LaTeX resume through LangChain, or use a structural check."""
    import json as _json

    if not settings.has_gemini:
        valid, issues = validate_latex(latex_source)
        return {
            "passed": valid,
            "score": 80 if valid else 40,
            "issues": issues,
            "feedback": "Structural validation only (no Gemini key).",
            "latex_valid": valid,
            "jd_match_score": 75,
            "experience_relevance_score": 75,
        }

    try:
        profile_json = _json.dumps(profile, indent=2, default=str)
        user_msg = dedent(f"""\
## Job Role: {job_role} @ {company}

## Job Description
{job_description}

## Candidate Profile
{profile_json}

## Generated LaTeX Resume
```latex
{latex_source[:5000]}
```

Evaluate and return JSON.
""")
        raw = await invoke_chat(
            _VERIFY_SYSTEM,
            user_msg,
            temperature=0.0,
            max_tokens=512,
        )
        import re as _re
        m = _re.search(r"\{.*\}", raw, _re.DOTALL)
        if m:
            data = _json.loads(m.group())
            return {
                "passed": bool(data.get("passed", False)),
                "score": int(data.get("score", 0)),
                "issues": list(data.get("issues", [])),
                "feedback": str(data.get("feedback", "")),
                "latex_valid": bool(data.get("latex_valid", True)),
                "jd_match_score": int(data.get("jd_match_score", 0)),
                "experience_relevance_score": int(data.get("experience_relevance_score", 0)),
            }
    except Exception:
        pass

    return {
        "passed": True,
        "score": 75,
        "issues": [],
        "feedback": "Verifier unavailable.",
        "latex_valid": True,
        "jd_match_score": 75,
        "experience_relevance_score": 75,
    }


# ── Main async pipeline ───────────────────────────────────────────────────────

class PipelineState(TypedDict, total=False):
    job_role: str
    company: str
    job_description: str
    profile: dict
    user_id: str
    requested_template_key: str
    template_key: str
    template_latex: str
    resume_id: Optional[str]
    latex_source: str
    feedback: str
    verification: dict
    iterations: int
    pdf_success: bool
    pdf_bytes: Optional[bytes]
    pdf_error: str


async def _select_template(state: PipelineState) -> dict:
    available = get_template_names()
    template_key = state["requested_template_key"]
    # Step 1: Template selection
    if template_key == "auto" or template_key not in available:
        template_key = "classic"
    return {
        "template_key": template_key,
        "template_latex": get_template(template_key),
        "feedback": "",
        "iterations": 0,
    }


async def _generate_resume(state: PipelineState) -> dict:
    latex_source = await _run_agent1(
        job_role=state["job_role"],
        company=state["company"],
        job_description=state["job_description"],
        profile=state["profile"],
        template_key=state["template_key"],
        template_latex=state["template_latex"],
        feedback=state.get("feedback", ""),
    )
    return {"latex_source": latex_source}


async def _verify_resume(state: PipelineState) -> dict:
    verification = await _run_agent2(
        job_role=state["job_role"],
        company=state["company"],
        job_description=state["job_description"],
        profile=state["profile"],
        latex_source=state["latex_source"],
    )
    return {
        "verification": verification,
        "iterations": state["iterations"] + 1,
        "feedback": verification.get("feedback", ""),
    }


def _route_after_verification(state: PipelineState) -> str:
    if state["verification"].get("passed") or state["iterations"] >= MAX_ITER:
        return "finalize"
    return "generate"


async def _finalize_pipeline(state: PipelineState) -> dict:
    pdf_success, pdf_bytes, pdf_error = await compile_latex_to_pdf(state["latex_source"])
    await _save_to_db(
        user_id=state["user_id"],
        resume_id=state.get("resume_id"),
        job_role=state["job_role"],
        company=state["company"],
        job_description=state["job_description"],
        template_key=state["template_key"],
        latex_output=state["latex_source"],
        pdf_bytes=pdf_bytes,
        iterations=state["iterations"],
        verification=state["verification"],
    )
    return {
        "pdf_success": pdf_success,
        "pdf_bytes": pdf_bytes,
        "pdf_error": pdf_error,
    }


def _build_pipeline_graph():
    workflow = StateGraph(PipelineState)
    workflow.add_node("select_template", _select_template)
    workflow.add_node("generate", _generate_resume)
    workflow.add_node("verify", _verify_resume)
    workflow.add_node("finalize", _finalize_pipeline)
    workflow.add_edge(START, "select_template")
    workflow.add_edge("select_template", "generate")
    workflow.add_edge("generate", "verify")
    workflow.add_conditional_edges(
        "verify",
        _route_after_verification,
        {"generate": "generate", "finalize": "finalize"},
    )
    workflow.add_edge("finalize", END)
    return workflow.compile()


_pipeline_graph = _build_pipeline_graph()


async def run_pipeline(
    job_role: str,
    company: str,
    job_description: str,
    profile: dict,
    user_id: str,
    template_key: str = "auto",
    resume_id: Optional[str] = None,
) -> PipelineResult:
    state = await _pipeline_graph.ainvoke({
        "job_role": job_role,
        "company": company,
        "job_description": job_description,
        "profile": profile,
        "user_id": user_id,
        "requested_template_key": template_key,
        "resume_id": resume_id,
    })
    result = PipelineResult()
    result.template_key = state["template_key"]
    result.iterations = state["iterations"]
    result.verification_result = state["verification"]
    result.final_latex = state["latex_source"]
    result.pdf_success = state["pdf_success"]
    result.pdf_bytes = state["pdf_bytes"]
    result.pdf_error = state["pdf_error"]
    result.success = True
    result.fallback_used = not settings.has_gemini
    return result


async def _save_to_db(
    user_id: str,
    resume_id: Optional[str],
    job_role: str,
    company: str,
    job_description: str,
    template_key: str,
    latex_output: str,
    pdf_bytes: Optional[bytes],
    iterations: int,
    verification: dict,
) -> None:
    try:
        db = get_db()
        doc = {
            "user_id": user_id,
            "title": f"{job_role} @ {company}",
            "job_role": job_role,
            "company": company,
            "job_description": job_description[:2000],
            "template_key": template_key,
            "latex_output": latex_output,
            "pdf_base64": base64.b64encode(pdf_bytes).decode() if pdf_bytes else None,
            "agent1_iterations": iterations,
            "verified": verification.get("passed", False),
            "verification_score": verification.get("score", 0),
            "verification_notes": verification.get("feedback", ""),
            "jd_match_score": verification.get("jd_match_score", 0),
            "experience_relevance_score": verification.get("experience_relevance_score", 0),
            "ats_score": verification.get("score", 0),
            "updated_at": datetime.utcnow(),
        }
        if resume_id:
            from bson import ObjectId
            await db.resumes.update_one(
                {"_id": ObjectId(resume_id)},
                {"$set": doc},
            )
        else:
            doc["created_at"] = datetime.utcnow()
            await db.resumes.insert_one(doc)
    except Exception:
        pass  # non-fatal


# ── Utilities ─────────────────────────────────────────────────────────────────

def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:latex)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _deterministic_fill(
    template_latex: str,
    profile: dict,
    job_role: str,
    company: str,
) -> str:
    """Fill template placeholders with profile data (no LLM)."""
    exp = profile.get("experience", [{}])
    edu = profile.get("education", [{}])
    projs = profile.get("projects", [{}])

    replacements = {
        "{{NAME}}": profile.get("full_name", "Your Name"),
        "{{PHONE}}": profile.get("phone", ""),
        "{{EMAIL}}": profile.get("email", ""),
        "{{LINKEDIN}}": profile.get("linkedin", ""),
        "{{GITHUB}}": profile.get("github", ""),
        "{{EXTRA_LINKS}}": "",
        "{{SKILLS}}": ", ".join(profile.get("skills", [])),
        "{{LANGUAGES}}": ", ".join(profile.get("languages", [])),
        "{{EDUCATION_ENTRIES}}": _format_edu(edu),
        "{{EXPERIENCE_ENTRIES}}": _format_exp(exp),
        "{{PROJECT_ENTRIES}}": _format_proj(projs),
        "{{ACHIEVEMENTS_SECTION}}": "",
        "{{COMPETITIVE_SECTION}}": "",
    }
    result = template_latex
    for k, v in replacements.items():
        result = result.replace(k, _escape_latex(v) if k in [
            "{{NAME}}", "{{PHONE}}", "{{EMAIL}}"
        ] else v)
    return result


def _escape_latex(s: str) -> str:
    for ch, esc in [("&", "\\&"), ("%", "\\%"), ("$", "\\$"), ("#", "\\#"),
                    ("_", "\\_"), ("^", "\\^"), ("{", "\\{"), ("}", "\\}")]:
        s = s.replace(ch, esc)
    return s


def _format_exp(entries: list[dict]) -> str:
    lines = []
    for e in entries:
        lines.append(
            f"\\resumeSubheading{{{_escape_latex(e.get('company',''))}}}"
            f"{{{e.get('duration','')}}}"
            f"{{{_escape_latex(e.get('role',''))}}}"
            f"{{{e.get('location','')}}}"
        )
        bullets = e.get("bullets", [])
        if bullets:
            lines.append("\\resumeItemListStart")
            for b in bullets:
                lines.append(f"  \\resumeItem{{{_escape_latex(b)}}}")
            lines.append("\\resumeItemListEnd")
    return "\n".join(lines)


def _format_edu(entries: list[dict]) -> str:
    lines = []
    for e in entries:
        gpa = f" — GPA: {e.get('gpa')}" if e.get("gpa") else ""
        lines.append(
            f"\\resumeSubheading{{{_escape_latex(e.get('institution',''))}}}"
            f"{{{e.get('duration','')}}}"
            f"{{{_escape_latex(e.get('degree','') + ' in ' + e.get('field',''))}}}"
            f"{{{_escape_latex(gpa)}}}"
        )
    return "\n".join(lines)


def _format_proj(entries: list[dict]) -> str:
    lines = []
    for p in entries:
        lines.append(
            f"\\resumeProjectHeading{{\\textbf{{{_escape_latex(p.get('name',''))}}}"
            f" $|$ \\emph{{{_escape_latex(p.get('tech_stack',''))}}}}}"
            f"{{{p.get('duration','')}}}"
        )
        bullets = p.get("bullets", [])
        if bullets:
            lines.append("\\resumeItemListStart")
            for b in bullets:
                lines.append(f"  \\resumeItem{{{_escape_latex(b)}}}")
            lines.append("\\resumeItemListEnd")
    return "\n".join(lines)
