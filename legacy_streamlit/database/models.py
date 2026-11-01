"""
database/models.py
Pydantic models that mirror the MongoDB documents.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel, Field
from bson import ObjectId


# ── Helpers ──────────────────────────────────────────────────────────────────

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        if ObjectId.is_valid(v):
            return str(v)
        raise ValueError("Invalid ObjectId")


# ── Experience / Education / Project sub-models ───────────────────────────────

class ExperienceEntry(BaseModel):
    company: str = ""
    role: str = ""
    duration: str = ""          # e.g. "Jan 2022 – Dec 2023"
    location: str = ""
    bullets: list[str] = Field(default_factory=list)


class EducationEntry(BaseModel):
    institution: str = ""
    degree: str = ""
    field: str = ""
    duration: str = ""
    gpa: str = ""
    bullets: list[str] = Field(default_factory=list)


class ProjectEntry(BaseModel):
    name: str = ""
    tech_stack: str = ""
    duration: str = ""
    bullets: list[str] = Field(default_factory=list)
    link: str = ""


class CertificationEntry(BaseModel):
    name: str = ""
    issuer: str = ""
    date: str = ""
    link: str = ""


class AchievementEntry(BaseModel):
    title: str = ""
    description: str = ""


# ── User document ─────────────────────────────────────────────────────────────

class UserInDB(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    username: str
    email: str
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


# ── Profile (internal details) ────────────────────────────────────────────────

class UserProfile(BaseModel):
    user_id: str                       # references UserInDB._id
    # Personal
    full_name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    # Online presence
    linkedin: str = ""
    github: str = ""
    leetcode: str = ""
    codeforces: str = ""
    portfolio: str = ""
    kaggle: str = ""
    twitter: str = ""
    # Extra custom links (list of {"label": str, "url": str})
    custom_links: list[dict[str, str]] = Field(default_factory=list)
    # Summary / Objective
    professional_summary: str = ""
    # Arrays
    experience: list[ExperienceEntry] = Field(default_factory=list)
    education: list[EducationEntry] = Field(default_factory=list)
    projects: list[ProjectEntry] = Field(default_factory=list)
    certifications: list[CertificationEntry] = Field(default_factory=list)
    achievements: list[AchievementEntry] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    # Meta
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()


# ── Resume history document ───────────────────────────────────────────────────

class ResumeHistory(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: str
    job_role: str
    company: str
    job_description: str
    template_used: str
    latex_output: str
    pdf_bytes: Optional[bytes] = None        # stored as GridFS or base64
    agent1_iterations: int = 0
    verified: bool = False
    verification_notes: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
