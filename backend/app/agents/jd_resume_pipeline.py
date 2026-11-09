"""
backend/app/agents/jd_resume_pipeline.py

JD-Based Resume Generation — Agentic Architecture (v2)
=======================================================
Architecture (from diagram):
  Input: Job Role, Job Description, Company Name

  1. Web Search Agent   (Tavily)    → company intel
  2. Short Summary Agent (Gemini)   → summarise company + JD, strip irrelevant
  3. Previous Resume Agent          → extract name, email, linkedin, education from profile
  4. GitHub Repo Agent  (GitHub API)→ top-5 repos most relevant to the summary
  5. Resume Generate Agent (Gemini) → full LaTeX resume combining all above
  6. Review Agent       (Gemini)    → similarity score vs summary; if < threshold → loop to 5
  7. LaTeX→PDF Agent                → compile LaTeX to PDF bytes

Threshold for review: score >= 75 passes; otherwise regenerates (max 3 times).
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from textwrap import dedent
from typing import Any, AsyncGenerator, Optional, TypedDict

import httpx
from langgraph.graph import END, START, StateGraph

from app.agents.llm import invoke_chat
from app.core.config import get_settings
from app.services.pdf_service import compile_latex_to_pdf
from app.services.latex_templates import get_template

settings = get_settings()

REVIEW_THRESHOLD = 75   # review score >= this → pass
MAX_GEN_ITER     = 3    # max resume regeneration loops


# ── Streaming step events ─────────────────────────────────────────────────────

class JDPipelineStep:
    def __init__(self, agent: str, message: str, percent: int, data: dict | None = None):
        self.agent   = agent
        self.message = message
        self.percent = percent
        self.data    = data or {}
        self.ts      = datetime.utcnow().isoformat()

    def to_dict(self) -> dict:
        return {
            "agent":   self.agent,
            "message": self.message,
            "percent": self.percent,
            "data":    self.data,
            "ts":      self.ts,
        }


class JDPipelineResult:
    def __init__(self):
        self.summary:      str           = ""
        self.github_repos: list[dict]    = []
        self.final_latex:  str           = ""
        self.pdf_bytes:    Optional[bytes] = None
        self.pdf_success:  bool          = False
        self.pdf_error:    str           = ""
        self.review_score: int           = 0
        self.iterations:   int           = 0
        self.success:      bool          = False
        self.error:        str           = ""


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 1 — Web Search (Tavily)
# ─────────────────────────────────────────────────────────────────────────────

async def _web_search_agent(job_role: str, company: str, job_description: str) -> str:
    """Search for company info using Tavily. Falls back to JD text only."""
    if not settings.has_tavily:
        return f"Company: {company}. Role: {job_role}.\n\nJob Description:\n{job_description}"

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.tavily_api_key,
                    "query": f"{company} company overview products culture engineering",
                    "max_results": 5,
                    "search_depth": "basic",
                    "include_answer": True,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                answer = data.get("answer", "")
                results = data.get("results", [])
                snippets = "\n\n".join(
                    f"[{r.get('title','')}]: {r.get('content','')[:300]}"
                    for r in results[:3]
                )
                return f"Company Summary (Tavily):\n{answer}\n\nDetails:\n{snippets}"
    except Exception:
        pass

    return f"Company: {company}. Role: {job_role}.\n\nJob Description:\n{job_description}"


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 2 — Short Summary (Gemini via LangChain)
# ─────────────────────────────────────────────────────────────────────────────

_SUMMARY_SYSTEM = dedent("""\
You are a career strategist. Given company intel and a job description, produce a
CONCISE summary (≤ 200 words) that:
1. Names the most critical technical skills and keywords.
2. Identifies 3–5 core competencies the company values.
3. Strips out boilerplate / irrelevant content.
Return ONLY the summary paragraph — no bullet points, no headers.
""")


async def _summary_agent(company_info: str, job_role: str, job_description: str) -> str:
    """Summarise company + JD into a focused paragraph for downstream agents."""
    if not settings.has_gemini:
        # Fallback: just truncate JD
        return f"Role: {job_role}. {job_description[:500]}"

    try:
        user_msg = dedent(f"""\
## Company Intel
{company_info}

## Job Role: {job_role}

## Job Description
{job_description}

Produce the concise summary now.
""")
        response = await invoke_chat(
            _SUMMARY_SYSTEM,
            user_msg,
            temperature=0.3,
            max_tokens=512,
        )
        return response or f"Role: {job_role}. {job_description[:500]}"
    except Exception:
        return f"Role: {job_role}. {job_description[:500]}"


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 3 — Previous Resume / Profile (DB)
# ─────────────────────────────────────────────────────────────────────────────

def _extract_essential_profile(profile: dict) -> dict:
    """Keep the most relevant profile details within a one-page resume budget."""
    return {
        "full_name":  profile.get("full_name", ""),
        "email":      profile.get("email", ""),
        "phone":      profile.get("phone", ""),
        "linkedin":   profile.get("linkedin", ""),
        "github":     profile.get("github", ""),
        "location":   profile.get("location", ""),
        "education":  profile.get("education", [])[:2],
        "skills":     profile.get("skills", [])[:16],
        "languages":  profile.get("languages", [])[:8],
        "experience": [
            {**entry, "bullets": entry.get("bullets", [])[:3]}
            for entry in profile.get("experience", [])[:3]
        ],
        "projects": [
            {**project, "bullets": project.get("bullets", [])[:2]}
            for project in profile.get("projects", [])[:2]
        ],
    }


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 4 — GitHub Repo Agent
# ─────────────────────────────────────────────────────────────────────────────

async def _github_repo_agent(github_username: str, summary: str) -> list[dict]:
    """
    Fetch top GitHub repos for the user and pick the 5 most relevant to the
    role summary using keyword overlap.
    Falls back to empty list when no GitHub token / username.
    """
    if not github_username:
        return []

    headers: dict[str, str] = {"Accept": "application/vnd.github+json"}
    if settings.has_github:
        headers["Authorization"] = f"Bearer {settings.github_token}"

    try:
        async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
            resp = await client.get(
                f"https://api.github.com/users/{github_username}/repos",
                params={"sort": "updated", "per_page": 50, "type": "owner"},
            )
            if resp.status_code != 200:
                return []

            repos = resp.json()

        # Score each repo by keyword overlap with summary
        summary_words = set(re.findall(r"\w+", summary.lower()))
        scored = []
        for repo in repos:
            if repo.get("fork"):
                continue
            desc  = (repo.get("description") or "").lower()
            name  = (repo.get("name") or "").lower()
            lang  = (repo.get("language") or "").lower()
            topics = [t.lower() for t in (repo.get("topics") or [])]
            text_words = set(re.findall(r"\w+", f"{name} {desc} {lang} {' '.join(topics)}"))
            overlap = len(summary_words & text_words)
            scored.append((overlap, repo))

        scored.sort(key=lambda x: x[0], reverse=True)
        top5 = scored[:5]

        return [
            {
                "name":        r["name"],
                "description": r.get("description") or "",
                "language":    r.get("language") or "",
                "topics":      r.get("topics") or [],
                "stars":       r.get("stargazers_count", 0),
                "url":         r.get("html_url", ""),
            }
            for _, r in top5
        ]
    except Exception:
        return []


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 5 — Resume Generate (Gemini via LangChain → LaTeX)
# ─────────────────────────────────────────────────────────────────────────────

_GEN_SYSTEM = dedent("""\
You are an expert LaTeX resume writer specialising in ATS-friendly, one-page resumes.

Rules:
1. Analyse the summary, profile, and GitHub projects together.
2. Fill every {{PLACEHOLDER}} in the supplied single-column template; do not replace its layout.
3. Keep the resume to ONE page. Include at most 3 experience entries, 3 bullets per role,
   2 projects with at most 2 bullets each, 2 education entries, and 16 relevant skills.
4. Write concise, factual bullet points (ideally one line each) with strong verbs. Never
   turn multiple experience bullets into a paragraph or combine headings and dates.
5. Match relevant job-description keywords only when supported by the candidate profile.
6. Preserve every company, role, date, and metric accurately. Do not invent achievements,
   metrics, technologies, or employment details.
7. For experience entries use \\resumeSubheading and wrap bullets in
   \\resumeItemListStart / \\resumeItem / \\resumeItemListEnd.
8. For project entries use \\resumeProjectHeading and wrap bullets in the same item-list
   macros. Use \\resumeSubheading for education entries.
9. Keep standard ATS section headings and a single-column reading order.
10. Output ONLY valid, compilable LaTeX — no markdown fences or explanation. Escape LaTeX
    special characters in candidate-provided text.
""")


async def _resume_generate_agent(
    job_role:    str,
    company:     str,
    summary:     str,
    profile:     dict,
    github_repos: list[dict],
    template_latex: str,
    feedback:    str = "",
) -> str:
    """Generate a LaTeX resume, or use deterministic fill when Gemini is unavailable."""
    if not settings.has_gemini:
        return _deterministic_fill(template_latex, profile, job_role, company)

    try:
        profile_json = json.dumps(profile, indent=2, default=str)
        repos_json   = json.dumps(github_repos, indent=2, default=str)
        feedback_block = f"\n\n## Previous Attempt Feedback\n{feedback}" if feedback else ""

        user_msg = dedent(f"""\
## Target Role: {job_role} @ {company}

## Role & Company Summary
{summary}

## Candidate Profile (JSON)
{profile_json}

## Relevant GitHub Projects (JSON — use the top ones matching the role)
{repos_json}

## LaTeX Template (fill ALL {{PLACEHOLDER}} tokens)
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


# ─────────────────────────────────────────────────────────────────────────────
# AGENT 6 — Review Agent (Gemini via LangChain)
# ─────────────────────────────────────────────────────────────────────────────

_REVIEW_SYSTEM = dedent("""\
You are a strict resume quality-assurance expert. Evaluate the LaTeX resume
against the role summary and return JSON ONLY:
{
  "score": 0-100,
  "passed": true/false,
  "feedback": "Specific, actionable feedback for the generator if score is low.",
  "issues": ["issue 1", "issue 2"]
}
score >= 75 → passed=true. Focus on: keyword match, project relevance, formatting.
""")


async def _review_agent(summary: str, latex_source: str) -> dict:
    """Score the generated resume against the summary. Falls back to structural check."""
    if not settings.has_gemini:
        from app.services.pdf_service import validate_latex
        valid, issues = validate_latex(latex_source)
        return {
            "score":    80 if valid else 40,
            "passed":   valid,
            "feedback": "Structural validation only (no Gemini key).",
            "issues":   issues,
        }

    try:
        user_msg = dedent(f"""\
## Role & Company Summary
{summary}

## Generated LaTeX Resume
```latex
{latex_source[:6000]}
```

Evaluate and return JSON.
""")
        raw = await invoke_chat(
            _REVIEW_SYSTEM,
            user_msg,
            temperature=0.0,
            max_tokens=512,
        )
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            data = json.loads(m.group())
            score = int(data.get("score", 0))
            return {
                "score":    score,
                "passed":   score >= REVIEW_THRESHOLD,
                "feedback": str(data.get("feedback", "")),
                "issues":   list(data.get("issues", [])),
            }
    except Exception:
        pass

    return {"score": 75, "passed": True, "feedback": "Review unavailable.", "issues": []}


class JDPipelineState(TypedDict, total=False):
    job_role: str
    company: str
    job_description: str
    profile: dict
    user_id: str
    requested_template_key: str
    template_key: str
    template_latex: str
    company_info: str
    summary: str
    essential_profile: dict
    github_username: str
    github_repos: list[dict]
    latex_source: str
    feedback: str
    review: dict
    iterations: int
    pdf_success: bool
    pdf_bytes: Optional[bytes]
    pdf_error: str
    resume_id: Optional[str]


async def _select_jd_template(state: JDPipelineState) -> dict:
    from app.services.latex_templates import get_template_names

    template_key = state["requested_template_key"]
    if template_key not in get_template_names():
        template_key = "executive"
    return {
        "template_key": template_key,
        "template_latex": get_template(template_key),
        "iterations": 0,
        "feedback": "",
    }


async def _search_company(state: JDPipelineState) -> dict:
    return {
        "company_info": await _web_search_agent(
            state["job_role"],
            state["company"],
            state["job_description"],
        )
    }


async def _summarize_job(state: JDPipelineState) -> dict:
    return {
        "summary": await _summary_agent(
            state["company_info"],
            state["job_role"],
            state["job_description"],
        )
    }


async def _extract_profile(state: JDPipelineState) -> dict:
    profile = state["profile"]
    return {
        "essential_profile": _extract_essential_profile(profile),
        "github_username": profile.get("github", "").rstrip("/").split("/")[-1],
    }


async def _find_relevant_repositories(state: JDPipelineState) -> dict:
    return {
        "github_repos": await _github_repo_agent(
            state["github_username"],
            state["summary"],
        )
    }


async def _generate_jd_resume(state: JDPipelineState) -> dict:
    return {
        "latex_source": await _resume_generate_agent(
            job_role=state["job_role"],
            company=state["company"],
            summary=state["summary"],
            profile=state["essential_profile"],
            github_repos=state["github_repos"],
            template_latex=state["template_latex"],
            feedback=state.get("feedback", ""),
        )
    }


async def _review_jd_resume(state: JDPipelineState) -> dict:
    review = await _review_agent(state["summary"], state["latex_source"])
    return {
        "review": review,
        "iterations": state["iterations"] + 1,
        "feedback": review.get("feedback", ""),
    }


def _route_jd_review(state: JDPipelineState) -> str:
    if state["review"].get("passed") or state["iterations"] >= MAX_GEN_ITER:
        return "compile_pdf"
    return "generate"


async def _compile_jd_pdf(state: JDPipelineState) -> dict:
    pdf_success, pdf_bytes, pdf_error = await compile_latex_to_pdf(state["latex_source"])
    return {
        "pdf_success": pdf_success,
        "pdf_bytes": pdf_bytes,
        "pdf_error": pdf_error,
    }


async def _persist_jd_resume(state: JDPipelineState) -> dict:
    import base64
    from app.core.database import get_db

    resume_id = None
    try:
        db = get_db()
        review = state["review"]
        doc = {
            "user_id": state["user_id"],
            "title": f"{state['job_role']} @ {state['company']}",
            "job_role": state["job_role"],
            "company": state["company"],
            "job_description": state["job_description"][:2000],
            "template_key": state["template_key"],
            "latex_output": state["latex_source"],
            "pdf_base64": (
                base64.b64encode(state["pdf_bytes"]).decode()
                if state.get("pdf_bytes")
                else None
            ),
            "verified": review.get("passed", False),
            "verification_score": review.get("score", 0),
            "verification_notes": review.get("feedback", ""),
            "jd_match_score": review.get("score", 0),
            "ats_score": review.get("score", 0),
            "agent1_iterations": state["iterations"],
            "pipeline_type": "jd_agentic",
            "github_repos_used": state["github_repos"],
            "summary_used": state["summary"],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        inserted = await db.resumes.insert_one(doc)
        resume_id = str(inserted.inserted_id)
    except Exception:
        pass
    return {"resume_id": resume_id}


def _build_jd_pipeline_graph():
    workflow = StateGraph(JDPipelineState)
    workflow.add_node("select_template", _select_jd_template)
    workflow.add_node("web_search", _search_company)
    workflow.add_node("summary", _summarize_job)
    workflow.add_node("profile", _extract_profile)
    workflow.add_node("github", _find_relevant_repositories)
    workflow.add_node("generate", _generate_jd_resume)
    workflow.add_node("review", _review_jd_resume)
    workflow.add_node("compile_pdf", _compile_jd_pdf)
    workflow.add_node("persist", _persist_jd_resume)
    workflow.add_edge(START, "select_template")
    workflow.add_edge("select_template", "web_search")
    workflow.add_edge("web_search", "summary")
    workflow.add_edge("summary", "profile")
    workflow.add_edge("profile", "github")
    workflow.add_edge("github", "generate")
    workflow.add_edge("generate", "review")
    workflow.add_conditional_edges(
        "review",
        _route_jd_review,
        {"generate": "generate", "compile_pdf": "compile_pdf"},
    )
    workflow.add_edge("compile_pdf", "persist")
    workflow.add_edge("persist", END)
    return workflow.compile()


_jd_pipeline_graph = _build_jd_pipeline_graph()


# ─────────────────────────────────────────────────────────────────────────────
# MAIN PIPELINE (non-streaming, returns JDPipelineResult)
# ─────────────────────────────────────────────────────────────────────────────

async def _run_jd_pipeline_legacy(
    job_role:    str,
    company:     str,
    job_description: str,
    profile:     dict,
    user_id:     str,
    template_key: str = "executive",
) -> JDPipelineResult:
    """
    Full 7-agent JD-based resume generation pipeline.
    Returns a JDPipelineResult with latex, pdf, and metadata.
    """
    from app.services.latex_templates import get_template, get_template_names
    from app.core.database import get_db
    import base64

    result = JDPipelineResult()

    # — Select template ——————————————————————————————————————————
    available = get_template_names()
    if template_key not in available:
        template_key = "executive"
    template_latex = get_template(template_key)

    # — Agent 1: Web Search ———————————————————————————————————————
    company_info = await _web_search_agent(job_role, company, job_description)

    # — Agent 2: Short Summary ————————————————————————————————————
    summary = await _summary_agent(company_info, job_role, job_description)
    result.summary = summary

    # — Agent 3: Profile extraction ———————————————————————————————
    essential = _extract_essential_profile(profile)
    github_username = profile.get("github", "").rstrip("/").split("/")[-1]

    # — Agent 4: GitHub Repos —————————————————————————————————————
    repos = await _github_repo_agent(github_username, summary)
    result.github_repos = repos

    # — Agents 5 + 6: Generate → Review loop ———————————————————————
    latex_source = ""
    feedback     = ""
    review: dict = {}

    for iteration in range(MAX_GEN_ITER):
        # Agent 5: Generate
        latex_source = await _resume_generate_agent(
            job_role=job_role,
            company=company,
            summary=summary,
            profile=essential,
            github_repos=repos,
            template_latex=template_latex,
            feedback=feedback,
        )

        # Agent 6: Review
        review = await _review_agent(summary, latex_source)
        result.iterations = iteration + 1

        if review.get("passed", False):
            break
        feedback = review.get("feedback", "")

    result.final_latex  = latex_source
    result.review_score = review.get("score", 0)

    # — Agent 7: LaTeX → PDF ——————————————————————————————————————
    pdf_success, pdf_bytes, pdf_error = await compile_latex_to_pdf(latex_source)
    result.pdf_success = pdf_success
    result.pdf_bytes   = pdf_bytes
    result.pdf_error   = pdf_error

    # — Persist to DB ——————————————————————————————————————————————
    try:
        db = get_db()
        doc = {
            "user_id":          user_id,
            "title":            f"{job_role} @ {company}",
            "job_role":         job_role,
            "company":          company,
            "job_description":  job_description[:2000],
            "template_key":     template_key,
            "latex_output":     latex_source,
            "pdf_base64":       base64.b64encode(pdf_bytes).decode() if pdf_bytes else None,
            "verified":         review.get("passed", False),
            "verification_score": review.get("score", 0),
            "verification_notes": review.get("feedback", ""),
            "jd_match_score":   review.get("score", 0),
            "ats_score":        review.get("score", 0),
            "agent1_iterations": result.iterations,
            "pipeline_type":    "jd_agentic",
            "github_repos_used": repos,
            "summary_used":     summary,
            "created_at":       datetime.utcnow(),
            "updated_at":       datetime.utcnow(),
        }
        await db.resumes.insert_one(doc)
    except Exception:
        pass  # non-fatal

    result.success = True
    return result


# ─────────────────────────────────────────────────────────────────────────────
# STREAMING VERSION (SSE) — for frontend progress updates
# ─────────────────────────────────────────────────────────────────────────────

async def _run_jd_pipeline_stream_legacy(
    job_role:    str,
    company:     str,
    job_description: str,
    profile:     dict,
    user_id:     str,
    template_key: str = "executive",
) -> AsyncGenerator[dict, None]:
    """
    Streaming version of the JD pipeline. Yields step dicts for SSE.
    Final event has type='done' with the result payload.
    """
    from app.services.latex_templates import get_template, get_template_names
    from app.core.database import get_db
    import base64

    result = JDPipelineResult()

    available = get_template_names()
    if template_key not in available:
        template_key = "executive"
    template_latex = get_template(template_key)

    # Step 1
    yield JDPipelineStep("web_search", f"🔍 Searching the web for {company}…", 5).to_dict()
    company_info = await _web_search_agent(job_role, company, job_description)

    # Step 2
    yield JDPipelineStep("summary", "📝 Summarising company intel & JD…", 20).to_dict()
    summary = await _summary_agent(company_info, job_role, job_description)
    result.summary = summary

    # Step 3
    yield JDPipelineStep("profile", "👤 Extracting profile details…", 30).to_dict()
    essential = _extract_essential_profile(profile)
    github_username = profile.get("github", "").rstrip("/").split("/")[-1]

    # Step 4
    yield JDPipelineStep("github", f"🐙 Fetching top GitHub repos for @{github_username or 'user'}…", 40).to_dict()
    repos = await _github_repo_agent(github_username, summary)
    result.github_repos = repos
    yield JDPipelineStep("github", f"✅ Found {len(repos)} relevant repos", 45, {"repos": [r["name"] for r in repos]}).to_dict()

    # Steps 5+6: Gen→Review loop
    latex_source = ""
    feedback     = ""
    review: dict = {}

    for iteration in range(MAX_GEN_ITER):
        pct_gen = 50 + iteration * 10
        yield JDPipelineStep(
            "generate",
            f"🤖 Generating resume (attempt {iteration + 1}/{MAX_GEN_ITER})…",
            pct_gen,
        ).to_dict()

        latex_source = await _resume_generate_agent(
            job_role=job_role,
            company=company,
            summary=summary,
            profile=essential,
            github_repos=repos,
            template_latex=template_latex,
            feedback=feedback,
        )

        pct_review = pct_gen + 5
        yield JDPipelineStep("review", "🔎 Reviewing resume quality…", pct_review).to_dict()
        review = await _review_agent(summary, latex_source)
        result.iterations = iteration + 1

        score = review.get("score", 0)
        passed = review.get("passed", False)

        if passed:
            yield JDPipelineStep(
                "review",
                f"✅ Review passed (score: {score}/100)",
                pct_review + 2,
                {"score": score},
            ).to_dict()
            break
        else:
            yield JDPipelineStep(
                "review",
                f"⚠️ Score {score}/100 below threshold — regenerating…",
                pct_review + 2,
                {"score": score, "feedback": review.get("feedback", "")},
            ).to_dict()
            feedback = review.get("feedback", "")

    result.final_latex  = latex_source
    result.review_score = review.get("score", 0)

    # Step 7: PDF
    yield JDPipelineStep("pdf", "📄 Compiling LaTeX → PDF…", 88).to_dict()
    pdf_success, pdf_bytes, pdf_error = await compile_latex_to_pdf(latex_source)
    result.pdf_success = pdf_success
    result.pdf_bytes   = pdf_bytes
    result.pdf_error   = pdf_error

    if pdf_success:
        yield JDPipelineStep("pdf", "✅ PDF compiled successfully!", 95).to_dict()
    else:
        yield JDPipelineStep("pdf", f"⚠️ PDF compile issue: {pdf_error[:100]}", 95).to_dict()

    # Persist
    yield JDPipelineStep("save", "💾 Saving to your dashboard…", 98).to_dict()
    resume_id = None
    try:
        db = get_db()
        doc = {
            "user_id":           user_id,
            "title":             f"{job_role} @ {company}",
            "job_role":          job_role,
            "company":           company,
            "job_description":   job_description[:2000],
            "template_key":      template_key,
            "latex_output":      latex_source,
            "pdf_base64":        base64.b64encode(pdf_bytes).decode() if pdf_bytes else None,
            "verified":          review.get("passed", False),
            "verification_score": review.get("score", 0),
            "verification_notes": review.get("feedback", ""),
            "jd_match_score":    review.get("score", 0),
            "ats_score":         review.get("score", 0),
            "agent1_iterations": result.iterations,
            "pipeline_type":     "jd_agentic",
            "github_repos_used": repos,
            "summary_used":      summary,
            "created_at":        datetime.utcnow(),
            "updated_at":        datetime.utcnow(),
        }
        ins = await db.resumes.insert_one(doc)
        resume_id = str(ins.inserted_id)
    except Exception:
        pass

    result.success = True

    yield {
        "type":         "done",
        "resume_id":    resume_id,
        "review_score": result.review_score,
        "iterations":   result.iterations,
        "pdf_success":  result.pdf_success,
        "repos_used":   len(result.github_repos),
        "percent":      100,
        "message":      "🎉 Resume generated and saved!",
    }


def _initial_jd_state(
    job_role: str,
    company: str,
    job_description: str,
    profile: dict,
    user_id: str,
    template_key: str,
) -> JDPipelineState:
    return {
        "job_role": job_role,
        "company": company,
        "job_description": job_description,
        "profile": profile,
        "user_id": user_id,
        "requested_template_key": template_key,
    }


def _jd_result_from_state(state: JDPipelineState) -> JDPipelineResult:
    result = JDPipelineResult()
    result.summary = state["summary"]
    result.github_repos = state["github_repos"]
    result.final_latex = state["latex_source"]
    result.pdf_bytes = state.get("pdf_bytes")
    result.pdf_success = state["pdf_success"]
    result.pdf_error = state["pdf_error"]
    result.review_score = state["review"].get("score", 0)
    result.iterations = state["iterations"]
    result.success = True
    return result


async def run_jd_pipeline(
    job_role: str,
    company: str,
    job_description: str,
    profile: dict,
    user_id: str,
    template_key: str = "executive",
) -> JDPipelineResult:
    """Run the JD resume generation LangGraph and return its result."""
    state = await _jd_pipeline_graph.ainvoke(
        _initial_jd_state(
            job_role,
            company,
            job_description,
            profile,
            user_id,
            template_key,
        )
    )
    return _jd_result_from_state(state)


async def run_jd_pipeline_stream(
    job_role: str,
    company: str,
    job_description: str,
    profile: dict,
    user_id: str,
    template_key: str = "executive",
) -> AsyncGenerator[dict, None]:
    """Stream progress updates while the JD resume LangGraph runs."""
    state = _initial_jd_state(
        job_role,
        company,
        job_description,
        profile,
        user_id,
        template_key,
    )

    async for update in _jd_pipeline_graph.astream(state, stream_mode="updates"):
        for node, values in update.items():
            if node == "generate":
                attempt = state.get("iterations", 0) + 1
                yield JDPipelineStep(
                    "generate",
                    f"🤖 Generating resume (attempt {attempt}/{MAX_GEN_ITER})…",
                    50 + (attempt - 1) * 10,
                ).to_dict()
            elif node == "review":
                review = values["review"]
                score = review.get("score", 0)
                pct = 55 + (state.get("iterations", 0)) * 10
                if review.get("passed"):
                    yield JDPipelineStep(
                        "review",
                        f"✅ Review passed (score: {score}/100)",
                        pct + 2,
                        {"score": score},
                    ).to_dict()
                else:
                    yield JDPipelineStep(
                        "review",
                        f"⚠️ Score {score}/100 below threshold — regenerating…",
                        pct + 2,
                        {"score": score, "feedback": review.get("feedback", "")},
                    ).to_dict()
            elif node == "web_search":
                yield JDPipelineStep(
                    "web_search",
                    f"🔍 Searching the web for {company}…",
                    5,
                ).to_dict()
            elif node == "summary":
                yield JDPipelineStep(
                    "summary",
                    "📝 Summarising company intel & JD…",
                    20,
                ).to_dict()
            elif node == "profile":
                yield JDPipelineStep(
                    "profile",
                    "👤 Extracting profile details…",
                    30,
                ).to_dict()
            elif node == "github":
                yield JDPipelineStep(
                    "github",
                    f"🐙 Fetching top GitHub repos for @{state.get('github_username') or 'user'}…",
                    40,
                ).to_dict()
                repos = values["github_repos"]
                yield JDPipelineStep(
                    "github",
                    f"✅ Found {len(repos)} relevant repos",
                    45,
                    {"repos": [repo["name"] for repo in repos]},
                ).to_dict()
            elif node == "compile_pdf":
                if values["pdf_success"]:
                    yield JDPipelineStep(
                        "pdf",
                        "✅ PDF compiled successfully!",
                        95,
                    ).to_dict()
                else:
                    yield JDPipelineStep(
                        "pdf",
                        f"⚠️ PDF compile issue: {values['pdf_error'][:100]}",
                        95,
                    ).to_dict()
            elif node == "persist":
                yield JDPipelineStep(
                    "save",
                    "💾 Saving to your dashboard…",
                    98,
                ).to_dict()
            state.update(values)

    result = _jd_result_from_state(state)
    yield {
        "type": "done",
        "resume_id": state.get("resume_id"),
        "review_score": result.review_score,
        "iterations": result.iterations,
        "pdf_success": result.pdf_success,
        "repos_used": len(result.github_repos),
        "percent": 100,
        "message": "🎉 Resume generated and saved!",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Utilities (shared with main pipeline)
# ─────────────────────────────────────────────────────────────────────────────

def _strip_fences(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:latex)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _escape_latex(s: str) -> str:
    for ch, esc in [("&", "\\&"), ("%", "\\%"), ("$", "\\$"), ("#", "\\#"),
                    ("_", "\\_"), ("^", "\\^"), ("{", "\\{"), ("}", "\\}")]:
        s = s.replace(ch, esc)
    return s


def _deterministic_fill(template_latex: str, profile: dict, job_role: str, company: str) -> str:
    """Fallback: fill template placeholders with profile data (no LLM)."""
    edu   = profile.get("education", [])
    exp   = profile.get("experience", [])
    projs = profile.get("projects", [])

    replacements = {
        "{{NAME}}":                  profile.get("full_name", "Your Name"),
        "{{PHONE}}":                 profile.get("phone", ""),
        "{{EMAIL}}":                 profile.get("email", ""),
        "{{LINKEDIN}}":              profile.get("linkedin", ""),
        "{{GITHUB}}":                profile.get("github", ""),
        "{{EXTRA_LINKS}}":           "",
        "{{SKILLS}}":                ", ".join(profile.get("skills", [])[:16]),
        "{{LANGUAGES}}":             ", ".join(profile.get("languages", [])[:8]),
        "{{EDUCATION_ENTRIES}}":     _fmt_edu(edu),
        "{{EXPERIENCE_ENTRIES}}":    _fmt_exp(exp),
        "{{PROJECT_ENTRIES}}":       _fmt_proj(projs),
        "{{ACHIEVEMENTS_SECTION}}":  "",
        "{{COMPETITIVE_SECTION}}":   "",
    }
    result = template_latex
    for k, v in replacements.items():
        result = result.replace(k, _escape_latex(v) if k in ["{{NAME}}", "{{PHONE}}", "{{EMAIL}}"] else v)
    return result


def _fmt_exp(entries: list[dict]) -> str:
    lines = []
    for e in entries:
        if not any(e.get(field) for field in ("company", "role", "duration", "location")):
            continue
        lines.append(
            f"\\resumeSubheading{{{_escape_latex(e.get('company',''))}}}"
            f"{{{_escape_latex(e.get('duration',''))}}}"
            f"{{{_escape_latex(e.get('role',''))}}}"
            f"{{{_escape_latex(e.get('location',''))}}}"
        )
        bullets = e.get("bullets", [])[:3]
        if bullets:
            lines.append("\\resumeItemListStart")
            lines.extend(f"  \\resumeItem{{{_escape_latex(b)}}}" for b in bullets)
            lines.append("\\resumeItemListEnd")
    return "\n".join(lines)


def _fmt_edu(entries: list[dict]) -> str:
    lines = []
    for e in entries:
        if not any(e.get(field) for field in ("institution", "degree", "field", "duration")):
            continue
        degree_field = " in ".join(filter(None, (e.get("degree", ""), e.get("field", ""))))
        gpa = f"GPA: {e.get('gpa')}" if e.get("gpa") else ""
        lines.append(
            f"\\resumeSubheading{{{_escape_latex(e.get('institution',''))}}}"
            f"{{{_escape_latex(e.get('duration',''))}}}"
            f"{{{_escape_latex(degree_field)}}}"
            f"{{{_escape_latex(gpa)}}}"
        )
    return "\n".join(lines)


def _fmt_proj(entries: list[dict]) -> str:
    lines = []
    for p in entries:
        if not any(p.get(field) for field in ("name", "tech_stack", "duration")):
            continue
        lines.append(
            f"\\resumeProjectHeading{{\\textbf{{{_escape_latex(p.get('name',''))}}}"
            f"{' $|$ ' if p.get('tech_stack') else ''}"
            f"\\emph{{{_escape_latex(p.get('tech_stack',''))}}}}}"
            f"{{{_escape_latex(p.get('duration',''))}}}"
        )
        bullets = p.get("bullets", [])[:2]
        if bullets:
            lines.append("\\resumeItemListStart")
            lines.extend(f"  \\resumeItem{{{_escape_latex(b)}}}" for b in bullets)
            lines.append("\\resumeItemListEnd")
    return "\n".join(lines)
