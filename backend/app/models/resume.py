"""
backend/app/models/resume.py
Pydantic v2 models for resume CRUD and history.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ── Create / Update ───────────────────────────────────────────────────────────

class ResumeCreateRequest(BaseModel):
    job_role: str = Field(..., min_length=1, max_length=200)
    company: str = Field(..., min_length=1, max_length=200)
    job_description: str = Field(..., min_length=1)
    template_key: str = "auto"
    title: Optional[str] = None  # user-friendly label


class ResumeUpdateRequest(BaseModel):
    job_role: Optional[str] = None
    company: Optional[str] = None
    job_description: Optional[str] = None
    template_key: Optional[str] = None
    title: Optional[str] = None
    # AI-generated content (stored after pipeline runs)
    latex_output: Optional[str] = None
    pdf_base64: Optional[str] = None
    agent1_iterations: Optional[int] = None
    verified: Optional[bool] = None
    verification_score: Optional[int] = None
    verification_notes: Optional[str] = None
    ats_score: Optional[int] = None
    jd_match_score: Optional[int] = None
    experience_relevance_score: Optional[int] = None


# ── DB document / response ────────────────────────────────────────────────────

class ResumeDocument(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    title: str = ""
    job_role: str = ""
    company: str = ""
    job_description: str = ""
    template_key: str = "classic"
    latex_output: str = ""
    pdf_base64: Optional[str] = None
    agent1_iterations: int = 0
    verified: bool = False
    verification_score: int = 0
    verification_notes: str = ""
    ats_score: int = 0
    jd_match_score: int = 0
    experience_relevance_score: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {"populate_by_name": True}


class ResumeListItem(BaseModel):
    """Lightweight list item — no latex/pdf blobs."""
    id: str
    title: str
    job_role: str
    company: str
    template_key: str
    verified: bool
    verification_score: int
    ats_score: int
    jd_match_score: int
    has_pdf: bool
    created_at: datetime
    updated_at: datetime
