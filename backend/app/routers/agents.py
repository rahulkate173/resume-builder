"""
backend/app/routers/agents.py
Agentic AI endpoints with streaming step feedback.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.agent import (
    ATSAuditRequest,
    ATSAuditResult,
    AgentRunResult,
    AgentStatus,
    GenerateSummaryRequest,
    GeneratedSummary,
    JDAnalysis,
    ParseJDRequest,
    RewriteBulletRequest,
    RewrittenBullet,
    TailorToJDRequest,
)
from app.agents.bullet_rewriter import rewrite_bullet
from app.agents.ats_auditor import audit_ats
from app.agents.jd_parser import parse_jd
from app.agents.summary_generator import generate_summary

settings = get_settings()
router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


def _make_run(agent: str) -> AgentRunResult:
    return AgentRunResult(
        run_id=str(uuid.uuid4()),
        agent=agent,
        status=AgentStatus.RUNNING,
        started_at=datetime.utcnow(),
        fallback_used=not settings.ai_available,
    )


# ── POST /agents/rewrite-bullet ───────────────────────────────────────────────

@router.post("/rewrite-bullet", response_model=AgentRunResult)
async def rewrite_bullet_endpoint(
    body: RewriteBulletRequest,
    current_user: dict = Depends(get_current_user),
):
    run = _make_run("bullet_rewriter")
    try:
        result: RewrittenBullet = await rewrite_bullet(
            bullet=body.bullet,
            job_role=body.job_role,
            job_description=body.job_description,
            context=body.context,
        )
        run.status = AgentStatus.DONE
        run.result = result.model_dump()
        run.fallback_used = not settings.has_groq
    except Exception as e:
        run.status = AgentStatus.FAILED
        run.error = str(e)
    finally:
        run.completed_at = datetime.utcnow()

    return run


# ── POST /agents/ats-audit ────────────────────────────────────────────────────

@router.post("/ats-audit", response_model=AgentRunResult)
async def ats_audit_endpoint(
    body: ATSAuditRequest,
    current_user: dict = Depends(get_current_user),
):
    run = _make_run("ats_auditor")

    # Load LaTeX from resume_id if provided
    latex_source = body.latex_source or ""
    if body.resume_id and not latex_source:
        db = get_db()
        try:
            doc = await db.resumes.find_one(
                {"_id": ObjectId(body.resume_id), "user_id": current_user["sub"]},
                {"latex_output": 1},
            )
            latex_source = doc.get("latex_output", "") if doc else ""
        except Exception:
            pass

    try:
        result: ATSAuditResult = await audit_ats(
            latex_source=latex_source,
            job_description=body.job_description,
        )
        run.status = AgentStatus.DONE
        run.result = result.model_dump()
        run.fallback_used = not settings.has_groq
    except Exception as e:
        run.status = AgentStatus.FAILED
        run.error = str(e)
    finally:
        run.completed_at = datetime.utcnow()

    return run


# ── POST /agents/tailor-to-jd ─────────────────────────────────────────────────

@router.post("/tailor-to-jd", response_model=AgentRunResult)
async def tailor_to_jd_endpoint(
    body: TailorToJDRequest,
    current_user: dict = Depends(get_current_user),
):
    run = _make_run("jd_parser")
    db = get_db()

    # Load resume + profile
    try:
        resume = await db.resumes.find_one(
            {"_id": ObjectId(body.resume_id), "user_id": current_user["sub"]}
        )
    except Exception:
        resume = None

    profile = await db.profiles.find_one({"user_id": current_user["sub"]}) or {}
    profile.pop("_id", None)

    try:
        result: JDAnalysis = await parse_jd(
            job_description=body.job_description,
            resume_skills=profile.get("skills", []) + profile.get("languages", []),
        )
        run.status = AgentStatus.DONE
        run.result = result.model_dump()
        run.fallback_used = not settings.has_groq
    except Exception as e:
        run.status = AgentStatus.FAILED
        run.error = str(e)
    finally:
        run.completed_at = datetime.utcnow()

    return run


# ── POST /agents/generate-summary ─────────────────────────────────────────────

@router.post("/generate-summary", response_model=AgentRunResult)
async def generate_summary_endpoint(
    body: GenerateSummaryRequest,
    current_user: dict = Depends(get_current_user),
):
    run = _make_run("summary_generator")
    db = get_db()

    # Load profile snapshot if not provided
    snap = body.profile_snapshot
    if not snap:
        profile = await db.profiles.find_one({"user_id": current_user["sub"]}) or {}
        profile.pop("_id", None)
        snap = profile

    try:
        result: GeneratedSummary = await generate_summary(
            job_role=body.job_role,
            job_description=body.job_description,
            seniority=body.seniority,
            profile_snapshot=snap,
        )
        run.status = AgentStatus.DONE
        run.result = result.model_dump()
        run.fallback_used = not settings.has_groq
    except Exception as e:
        run.status = AgentStatus.FAILED
        run.error = str(e)
    finally:
        run.completed_at = datetime.utcnow()

    return run


# ── GET /agents/models ────────────────────────────────────────────────────────

@router.get("/models")
async def get_model_status(current_user: dict = Depends(get_current_user)):
    """Return current AI model configuration and availability."""
    return {
        "agent1": {
            "model": settings.agent1_model,
            "provider": "Groq",
            "available": settings.has_groq,
        },
        "agent2": {
            "model": settings.groq_model,
            "provider": "Groq",
            "available": settings.has_groq,
        },
        "fallback": {
            "mode": "deterministic",
            "available": True,
            "description": "Rule-based heuristics — always available without API keys",
        },
    }
