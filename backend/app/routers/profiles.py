"""
backend/app/routers/profiles.py
Profile CRUD + PDF resume upload/parse endpoints.
"""

from __future__ import annotations

import io
from datetime import datetime
from textwrap import dedent
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.profile import ProfileUpdateRequest, UserProfile
from app.core.config import get_settings
from app.agents.llm import invoke_chat

router   = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])
settings = get_settings()


@router.get("/me")
async def get_my_profile(current_user: dict = Depends(get_current_user)):
    db = get_db()
    profile = await db.profiles.find_one({"user_id": current_user["sub"]})
    if not profile:
        # Create empty profile on first access
        empty = UserProfile(user_id=current_user["sub"]).model_dump()
        await db.profiles.insert_one(empty)
        profile = empty

    profile.pop("_id", None)
    return profile


@router.put("/me")
async def update_my_profile(
    body: ProfileUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    update_data = {
        k: v.model_dump() if hasattr(v, "model_dump") else
           ([item.model_dump() if hasattr(item, "model_dump") else item for item in v] if isinstance(v, list) else v)
        for k, v in body.model_dump(exclude_none=True).items()
    }
    update_data["user_id"] = current_user["sub"]
    update_data["updated_at"] = datetime.utcnow()

    result = await db.profiles.update_one(
        {"user_id": current_user["sub"]},
        {"$set": update_data},
        upsert=True,
    )
    if not result.acknowledged:
        raise HTTPException(status_code=500, detail="Failed to save profile.")

    profile = await db.profiles.find_one({"user_id": current_user["sub"]})
    profile.pop("_id", None)
    return profile


# ── POST /profiles/parse-resume ───────────────────────────────────────────────

_PARSE_SYSTEM = dedent("""\
You are an expert resume parser. Extract structured information from the resume text and return ONLY valid JSON with these exact fields (use empty strings/arrays if not found):
{
  "full_name": "",
  "email": "",
  "phone": "",
  "location": "",
  "linkedin": "",
  "github": "",
  "portfolio": "",
  "professional_summary": "",
  "skills": ["skill1", "skill2"],
  "languages": ["Python", "JavaScript"],
  "education": [
    {"institution": "", "degree": "", "field": "", "duration": "", "gpa": "", "bullets": []}
  ],
  "experience": [
    {"company": "", "role": "", "duration": "", "location": "", "bullets": ["achievement1"]}
  ],
  "projects": [
    {"name": "", "tech_stack": "", "duration": "", "bullets": ["description"], "link": ""}
  ],
  "certifications": [
    {"name": "", "issuer": "", "date": "", "link": ""}
  ],
  "achievements": [
    {"title": "", "description": ""}
  ]
}
Extract ALL work experience, projects, and education entries. For bullets, write concise action-verb sentences.
""")


@router.post("/parse-resume")
async def parse_resume_upload(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload a PDF or plain-text resume.
    Extracts text → Gemini via LangChain parses into structured profile JSON.
    Returns parsed data WITHOUT auto-saving (user confirms first).
    """
    # Validate file type
    allowed = {"application/pdf", "text/plain"}
    fname   = (file.filename or "").lower()
    ct      = file.content_type or ""
    if ct not in allowed and not fname.endswith((".pdf", ".txt")):
        raise HTTPException(
            status_code=400,
            detail="Only PDF or plain-text (.txt) files are supported.",
        )

    raw = await file.read()
    if len(raw) > 5 * 1024 * 1024:  # 5 MB limit
        raise HTTPException(status_code=400, detail="File too large (max 5 MB).")

    # ── Extract text ──────────────────────────────────────────────────────────
    text = ""
    if fname.endswith(".pdf") or ct == "application/pdf":
        text = _extract_pdf_text(raw)
    else:
        text = raw.decode("utf-8", errors="ignore")

    text = text.strip()
    if len(text) < 50:
        raise HTTPException(
            status_code=422,
            detail="Could not extract readable text from the file. Please try a text-selectable PDF.",
        )

    # Truncate to fit LLM context
    text = text[:8000]

    # ── Parse with Gemini via LangChain ────────────────────────────────────────
    parsed = await _gemini_parse(text)

    return {
        "parsed": parsed,
        "char_count": len(text),
        "message": "Resume parsed successfully. Review and save below.",
    }


def _extract_pdf_text(raw: bytes) -> str:
    """Extract plain text from PDF bytes using pdfplumber."""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(raw)) as pdf:
            pages = []
            for page in pdf.pages:
                t = page.extract_text() or ""
                pages.append(t)
            return "\n".join(pages)
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"PDF text extraction failed: {e}. Try a text-selectable PDF.",
        )


async def _gemini_parse(text: str) -> dict:
    """Send resume text to Gemini through LangChain and return profile data."""
    import json, re

    if not settings.has_gemini:
        raise HTTPException(
            status_code=503,
            detail="Gemini API key not configured. Set GEMINI_API_KEY in .env",
        )

    try:
        raw = await invoke_chat(
            _PARSE_SYSTEM,
            f"Parse this resume:\n\n{text}",
            temperature=0.1,
            max_tokens=4096,
        )
        # Strip markdown fences if present
        raw = re.sub(r"^```(?:json)?\s*", "", raw.strip(), flags=re.IGNORECASE)
        raw = re.sub(r"\s*```$", "", raw)
        # Find the JSON object
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            return json.loads(m.group())
    except json.JSONDecodeError:
        raise HTTPException(status_code=422, detail="LLM returned invalid JSON. Please try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini parsing failed: {e}")

    raise HTTPException(status_code=422, detail="Could not parse resume structure.")
