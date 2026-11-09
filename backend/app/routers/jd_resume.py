"""
backend/app/routers/jd_resume.py
JD-Based Resume Generation endpoint with SSE streaming.
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.core.database import get_db
from app.core.security import get_current_user
from app.agents.jd_resume_pipeline import run_jd_pipeline_stream

router = APIRouter(prefix="/api/v1/jd-resume", tags=["jd-resume"])


class JDResumeRequest(BaseModel):
    job_role:        str = Field(..., min_length=1, max_length=200)
    company:         str = Field(..., min_length=1, max_length=200)
    job_description: str = Field(..., min_length=10, max_length=10000)
    template_key:    str = "executive"


# ── POST /jd-resume/generate  (SSE streaming) ─────────────────────────────────

@router.post("/generate")
async def generate_jd_resume(
    body: JDResumeRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Start the 7-agent JD-based resume pipeline.
    Returns Server-Sent Events (text/event-stream) with pipeline progress.

    Each event is a JSON line:
      { agent, message, percent, data, ts }

    Final event has type="done" and includes resume_id.
    """
    db      = get_db()
    user_id = current_user["sub"]

    # Load user profile
    profile = await db.profiles.find_one({"user_id": user_id}) or {}
    profile.pop("_id", None)

    async def event_stream():
        try:
            async for step in run_jd_pipeline_stream(
                job_role=body.job_role,
                company=body.company,
                job_description=body.job_description,
                profile=profile,
                user_id=user_id,
                template_key=body.template_key,
            ):
                yield f"data: {json.dumps(step)}\n\n"
        except Exception as e:
            err = {"type": "error", "message": str(e), "percent": 0}
            yield f"data: {json.dumps(err)}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control":  "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
