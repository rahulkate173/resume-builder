"""
backend/app/models/profile.py
Pydantic v2 models for user profile (resume data).
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ExperienceEntry(BaseModel):
    company: str = ""
    role: str = ""
    duration: str = ""
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


class CustomLink(BaseModel):
    label: str = ""
    url: str = ""


# ── Full profile ──────────────────────────────────────────────────────────────

class UserProfile(BaseModel):
    user_id: str
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
    custom_links: list[CustomLink] = Field(default_factory=list)
    # Summary
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

    model_config = {"populate_by_name": True}


# ── Update request (partial) ──────────────────────────────────────────────────

class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    leetcode: Optional[str] = None
    codeforces: Optional[str] = None
    portfolio: Optional[str] = None
    kaggle: Optional[str] = None
    twitter: Optional[str] = None
    custom_links: Optional[list[CustomLink]] = None
    professional_summary: Optional[str] = None
    experience: Optional[list[ExperienceEntry]] = None
    education: Optional[list[EducationEntry]] = None
    projects: Optional[list[ProjectEntry]] = None
    certifications: Optional[list[CertificationEntry]] = None
    achievements: Optional[list[AchievementEntry]] = None
    skills: Optional[list[str]] = None
    languages: Optional[list[str]] = None
