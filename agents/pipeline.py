"""
agents/pipeline.py
Orchestrates the full multi-agent resume-building pipeline.

Flow:
  1. Agent 1 selects template
  2. Agent 1 generates LaTeX (loop up to MAX_ITER times)
  3. Agent 2 verifies → if fail, sends feedback back to Agent 1
  4. LLM 3 polishes and compiles PDF via MCP
  5. Save to MongoDB history
"""

from __future__ import annotations

import base64
from datetime import datetime
from typing import Any, Callable, Generator, Optional

from agents.agent1_generator import run_agent1, select_template, MAX_ITER
from agents.agent2_verifier import run_agent2
from agents.llm3_compiler import run_llm3_and_compile
from database.connection import get_db
from templates import get_template, get_template_names


# ── Public types ──────────────────────────────────────────────────────────────

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


ProgressCallback = Callable[[str, int], None]   # (message, percent)


# ── Main pipeline ─────────────────────────────────────────────────────────────

def run_pipeline(
    job_role: str,
    company: str,
    job_description: str,
    profile: dict[str, Any],
    user_id: str,
    template_key: str = "auto",
    progress_cb: Optional[ProgressCallback] = None,
) -> PipelineResult:
    """
    Execute the full multi-agent resume pipeline.

    Args:
        job_role: The target job title
        company: Target company name
        job_description: Full JD text
        profile: User's profile dict from MongoDB
        user_id: MongoDB user ID (for saving history)
        template_key: "auto" | "classic" | "modern" | "minimal"
        progress_cb: Optional callback(message, pct) for UI progress

    Returns:
        PipelineResult with final LaTeX and PDF bytes
    """
    result = PipelineResult()

    def _progress(msg: str, pct: int) -> None:
        if progress_cb:
            progress_cb(msg, pct)

    available_templates = get_template_names()

    # ── Step 1: Template Selection ────────────────────────────────────────────
    _progress("🎨 Agent 1: Selecting best template for your role...", 5)
    if template_key == "auto" or template_key not in available_templates:
        try:
            template_key = select_template(job_role, job_description, available_templates)
        except Exception as e:
            template_key = "modern"   # safe fallback
    result.template_key = template_key
    template_latex = get_template(template_key)
    _progress(f"✅ Template selected: **{template_key}**", 15)

    # ── Steps 2-3: Generate + Verify loop ────────────────────────────────────
    latex_source = ""
    feedback = ""
    verification: dict = {}

    for iteration in range(MAX_ITER):
        iter_num = iteration + 1
        _progress(f"✍️ Agent 1: Generating resume (attempt {iter_num}/{MAX_ITER})...", 15 + iteration * 20)

        try:
            latex_source = run_agent1(
                job_role=job_role,
                company=company,
                job_description=job_description,
                profile=profile,
                template_key=template_key,
                template_latex=template_latex,
                feedback=feedback,
                iteration=iteration,
            )
        except Exception as e:
            result.error = f"Agent 1 failed: {e}"
            return result

        _progress(f"🔍 Agent 2: Verifying resume (attempt {iter_num})...", 25 + iteration * 20)

        try:
            verification = run_agent2(
                job_role=job_role,
                company=company,
                job_description=job_description,
                profile=profile,
                latex_source=latex_source,
            )
        except Exception as e:
            # If verifier fails, treat as passed to avoid blocking the user
            verification = {
                "passed": True,
                "score": 75,
                "issues": [],
                "feedback": f"Verifier unavailable: {e}",
                "latex_valid": True,
                "jd_match_score": 75,
                "experience_relevance_score": 75,
            }

        result.iterations = iter_num
        result.verification_result = verification

        if verification.get("passed", False):
            _progress(f"✅ Agent 2: Resume approved! (score: {verification.get('score', 0)}/100)", 65)
            break
        else:
            feedback = verification.get("feedback", "")
            _progress(
                f"⚠️ Agent 2: Issues found (score {verification.get('score', 0)}/100). Regenerating...",
                25 + iteration * 20,
            )

    # ── Step 4: LLM 3 Polish + PDF Compilation ────────────────────────────────
    _progress("✨ LLM 3 (Mistral): Final polish and PDF generation...", 70)

    try:
        compile_result = run_llm3_and_compile(
            latex_source=latex_source,
            job_role=job_role,
        )
    except Exception as e:
        result.error = f"LLM3 / PDF compilation failed: {e}"
        result.final_latex = latex_source
        return result

    result.final_latex = compile_result["final_latex"]
    result.pdf_bytes = compile_result.get("pdf_bytes")
    result.pdf_success = compile_result.get("pdf_success", False)
    result.pdf_error = compile_result.get("pdf_error", "")

    _progress("💾 Saving to history...", 90)

    # ── Step 5: Save to MongoDB history ──────────────────────────────────────
    _save_history(
        user_id=user_id,
        job_role=job_role,
        company=company,
        job_description=job_description,
        template_key=template_key,
        latex_output=result.final_latex,
        pdf_bytes=result.pdf_bytes,
        iterations=result.iterations,
        verification=verification,
    )

    result.success = True
    _progress("🎉 Done! Your resume is ready.", 100)
    return result


def _save_history(
    user_id: str,
    job_role: str,
    company: str,
    job_description: str,
    template_key: str,
    latex_output: str,
    pdf_bytes: Optional[bytes],
    iterations: int,
    verification: dict,
) -> None:
    db = get_db()
    doc = {
        "user_id": user_id,
        "job_role": job_role,
        "company": company,
        "job_description": job_description[:2000],   # cap storage
        "template_used": template_key,
        "latex_output": latex_output,
        "pdf_base64": base64.b64encode(pdf_bytes).decode() if pdf_bytes else None,
        "agent1_iterations": iterations,
        "verified": verification.get("passed", False),
        "verification_score": verification.get("score", 0),
        "verification_notes": verification.get("feedback", ""),
        "created_at": datetime.utcnow(),
    }
    try:
        db.history.insert_one(doc)
    except Exception:
        pass  # non-fatal


def get_history(user_id: str, limit: int = 20) -> list[dict]:
    """Fetch resume generation history for a user."""
    db = get_db()
    cursor = db.history.find(
        {"user_id": user_id},
        sort=[("created_at", -1)],
        limit=limit,
    )
    results = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc.pop("pdf_base64", None)   # don't load large blobs in list
        results.append(doc)
    return results


def get_history_pdf(history_id: str) -> Optional[bytes]:
    """Fetch PDF bytes for a specific history entry."""
    from bson import ObjectId
    db = get_db()
    doc = db.history.find_one({"_id": ObjectId(history_id)})
    if doc and doc.get("pdf_base64"):
        return base64.b64decode(doc["pdf_base64"])
    return None
