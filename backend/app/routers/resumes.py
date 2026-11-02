"""
backend/app/routers/resumes.py
Full Resume CRUD + export endpoints.
"""

from __future__ import annotations

import base64
from datetime import datetime
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.resume import ResumeCreateRequest, ResumeListItem, ResumeUpdateRequest
from app.agents.pipeline import run_pipeline
from app.services.pdf_service import compile_latex_to_pdf, generate_pdf_from_resume_doc

router = APIRouter(prefix="/api/v1/resumes", tags=["resumes"])


def _doc_to_list_item(doc: dict) -> ResumeListItem:
    return ResumeListItem(
        id=str(doc["_id"]),
        title=doc.get("title", f"{doc.get('job_role','')} @ {doc.get('company','')}"),
        job_role=doc.get("job_role", ""),
        company=doc.get("company", ""),
        template_key=doc.get("template_key", "classic"),
        verified=doc.get("verified", False),
        verification_score=doc.get("verification_score", 0),
        ats_score=doc.get("ats_score", 0),
        jd_match_score=doc.get("jd_match_score", 0),
        has_pdf=bool(doc.get("pdf_base64")),
        created_at=doc.get("created_at", datetime.utcnow()),
        updated_at=doc.get("updated_at", datetime.utcnow()),
    )


# ── GET /resumes ──────────────────────────────────────────────────────────────

@router.get("", response_model=list[ResumeListItem])
async def list_resumes(
    limit: int = 20,
    skip: int = 0,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    cursor = db.resumes.find(
        {"user_id": current_user["sub"]},
        {"pdf_base64": 0, "latex_output": 0},  # exclude blobs from list
    ).sort("created_at", -1).skip(skip).limit(limit)
    docs = await cursor.to_list(length=limit)
    return [_doc_to_list_item(d) for d in docs]


# ── POST /resumes ─────────────────────────────────────────────────────────────

@router.post("", status_code=status.HTTP_201_CREATED)
async def create_resume(
    body: ResumeCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a resume record and run the AI pipeline."""
    db = get_db()
    user_id = current_user["sub"]

    # Load profile for the pipeline
    profile = await db.profiles.find_one({"user_id": user_id}) or {}
    profile.pop("_id", None)

    # Run pipeline
    result = await run_pipeline(
        job_role=body.job_role,
        company=body.company,
        job_description=body.job_description,
        profile=profile,
        user_id=user_id,
        template_key=body.template_key,
    )

    if not result.success:
        raise HTTPException(status_code=500, detail=result.error or "Pipeline failed.")

    # Fetch the newly created record
    doc = await db.resumes.find_one(
        {"user_id": user_id},
        sort=[("created_at", -1)],
    )
    if not doc:
        raise HTTPException(status_code=500, detail="Resume record not found after creation.")

    doc["_id"] = str(doc["_id"])
    doc.pop("pdf_base64", None)
    return doc


# ── GET /resumes/{id} ─────────────────────────────────────────────────────────

@router.get("/{resume_id}")
async def get_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    try:
        doc = await db.resumes.find_one(
            {"_id": ObjectId(resume_id), "user_id": current_user["sub"]},
            {"pdf_base64": 0},
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid resume ID.")

    if not doc:
        raise HTTPException(status_code=404, detail="Resume not found.")

    doc["_id"] = str(doc["_id"])
    return doc


# ── PUT /resumes/{id} ─────────────────────────────────────────────────────────

@router.put("/{resume_id}")
async def update_resume(
    resume_id: str,
    body: ResumeUpdateRequest,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    update_data = body.model_dump(exclude_none=True)
    update_data["updated_at"] = datetime.utcnow()

    try:
        result = await db.resumes.update_one(
            {"_id": ObjectId(resume_id), "user_id": current_user["sub"]},
            {"$set": update_data},
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid resume ID.")

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Resume not found.")

    doc = await db.resumes.find_one(
        {"_id": ObjectId(resume_id)}, {"pdf_base64": 0}
    )
    doc["_id"] = str(doc["_id"])
    return doc


# ── DELETE /resumes/{id} ──────────────────────────────────────────────────────

@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    try:
        result = await db.resumes.delete_one(
            {"_id": ObjectId(resume_id), "user_id": current_user["sub"]}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid resume ID.")

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Resume not found.")


# ── POST /resumes/{id}/duplicate ──────────────────────────────────────────────

@router.post("/{resume_id}/duplicate", status_code=status.HTTP_201_CREATED)
async def duplicate_resume(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
):
    db = get_db()
    try:
        source = await db.resumes.find_one(
            {"_id": ObjectId(resume_id), "user_id": current_user["sub"]}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid resume ID.")

    if not source:
        raise HTTPException(status_code=404, detail="Resume not found.")

    clone = {k: v for k, v in source.items() if k != "_id"}
    clone["title"] = f"Copy of {clone.get('title', 'Resume')}"
    clone["created_at"] = datetime.utcnow()
    clone["updated_at"] = datetime.utcnow()

    result = await db.resumes.insert_one(clone)
    clone["_id"] = str(result.inserted_id)
    clone.pop("pdf_base64", None)
    return clone


# ── POST /resumes/{id}/export/pdf ─────────────────────────────────────────────

@router.post("/{resume_id}/export/pdf")
async def export_pdf(
    resume_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Export resume as PDF.
    Tier 1: cached pdf_base64  (instant)
    Tier 2: recompile LaTeX online (ytotech → latexonline)
    Tier 3: reportlab from profile data  (always works, no external deps)
    """
    db = get_db()
    try:
        doc = await db.resumes.find_one(
            {"_id": ObjectId(resume_id), "user_id": current_user["sub"]}
        )
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid resume ID.")

    if not doc:
        raise HTTPException(status_code=404, detail="Resume not found.")

    # ── Tier 1: cached PDF ────────────────────────────────────────────────────
    if doc.get("pdf_base64"):
        pdf_bytes = base64.b64decode(doc["pdf_base64"])
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="resume_{resume_id}.pdf"'},
        )

    # ── Tier 2: recompile LaTeX ───────────────────────────────────────────────
    latex = doc.get("latex_output", "")
    if latex:
        success, pdf_bytes, _ = await compile_latex_to_pdf(latex)
        if success and pdf_bytes:
            await db.resumes.update_one(
                {"_id": ObjectId(resume_id)},
                {"$set": {"pdf_base64": base64.b64encode(pdf_bytes).decode()}},
            )
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="resume_{resume_id}.pdf"'},
            )

    # ── Tier 3: reportlab from structured profile data ────────────────────────
    profile = await db.profiles.find_one({"user_id": current_user["sub"]}) or {}
    profile.pop("_id", None)
    doc_clean = {k: v for k, v in doc.items() if k != "_id"}

    success, pdf_bytes, err = await generate_pdf_from_resume_doc(doc_clean, profile)
    if not success or not pdf_bytes:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {err}")

    # Cache so subsequent downloads are instant
    await db.resumes.update_one(
        {"_id": ObjectId(resume_id)},
        {"$set": {"pdf_base64": base64.b64encode(pdf_bytes).decode()}},
    )

    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="resume_{resume_id}.pdf"'},
    )
