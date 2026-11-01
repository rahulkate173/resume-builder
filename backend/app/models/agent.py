"""
backend/app/models/agent.py
Pydantic v2 models for agentic AI request/response schemas.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


# ── Agent request schemas ─────────────────────────────────────────────────────

class RewriteBulletRequest(BaseModel):
    bullet: str = Field(..., min_length=1, max_length=1000)
    job_role: str = ""
    job_description: str = ""
    context: str = ""  # e.g. company, seniority


class ATSAuditRequest(BaseModel):
    resume_id: Optional[str] = None
    latex_source: Optional[str] = None  # raw LaTeX to audit
    job_description: str = ""


class TailorToJDRequest(BaseModel):
    resume_id: str
    job_description: str = Field(..., min_length=10)
    job_role: str = ""
    company: str = ""


class GenerateSummaryRequest(BaseModel):
    job_role: str = Field(..., min_length=1)
    job_description: str = ""
    seniority: str = "mid"  # junior | mid | senior | executive
    profile_snapshot: dict[str, Any] = Field(default_factory=dict)


class ParseJDRequest(BaseModel):
    job_description: str = Field(..., min_length=10)
    resume_id: Optional[str] = None


# ── Agent response schemas ────────────────────────────────────────────────────

class RewrittenBullet(BaseModel):
    original: str
    rewritten: str
    method: str = "XYZ"  # XYZ | STAR
    confidence: float = 0.0
    action_verb: str = ""


class ATSAuditResult(BaseModel):
    score: int = Field(ge=0, le=100)
    section_scores: dict[str, int] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    auto_fixes: list[dict[str, str]] = Field(default_factory=list)
    keyword_density: dict[str, int] = Field(default_factory=dict)
    missing_keywords: list[str] = Field(default_factory=list)
    passed: bool = False


class JDAnalysis(BaseModel):
    hard_skills: list[str] = Field(default_factory=list)
    soft_skills: list[str] = Field(default_factory=list)
    core_competencies: list[str] = Field(default_factory=list)
    required_years: Optional[int] = None
    seniority: str = ""
    match_matrix: dict[str, bool] = Field(default_factory=dict)
    match_score: int = 0
    missing_keywords: list[str] = Field(default_factory=list)


class GeneratedSummary(BaseModel):
    summary: str
    seniority: str
    tailored_for: str


# ── Agent run log ─────────────────────────────────────────────────────────────

class AgentRunStep(BaseModel):
    step: str
    status: AgentStatus
    message: str = ""
    data: Any = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentRunResult(BaseModel):
    run_id: str
    agent: str
    status: AgentStatus
    steps: list[AgentRunStep] = Field(default_factory=list)
    result: Any = None
    error: Optional[str] = None
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    fallback_used: bool = False
