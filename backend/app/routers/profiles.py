"""
backend/app/routers/profiles.py
Profile CRUD endpoints.
"""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.profile import ProfileUpdateRequest, UserProfile

router = APIRouter(prefix="/api/v1/profiles", tags=["profiles"])


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
