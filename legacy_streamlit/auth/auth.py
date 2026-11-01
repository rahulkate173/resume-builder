"""
auth/auth.py
Authentication utilities: password hashing, JWT tokens, session helpers.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
import streamlit as st
from bson import ObjectId

from config.settings import get_settings
from database.connection import get_db
from database.models import UserInDB, UserProfile


settings = get_settings()

# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ── JWT helpers ───────────────────────────────────────────────────────────────

def create_token(user_id: str, username: str) -> str:
    payload = {
        "sub": user_id,
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ── DB helpers ────────────────────────────────────────────────────────────────

def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    """Register a new user. Returns (success, message)."""
    db = get_db()
    if db.users.find_one({"username": username}):
        return False, "Username already exists."
    if db.users.find_one({"email": email}):
        return False, "Email already registered."
    user_doc = {
        "username": username,
        "email": email,
        "password_hash": hash_password(password),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }
    result = db.users.insert_one(user_doc)
    # Create empty profile
    profile_doc = UserProfile(user_id=str(result.inserted_id)).to_dict()
    db.profiles.insert_one(profile_doc)
    return True, "Account created successfully!"


def login_user(username: str, password: str) -> tuple[bool, str, Optional[str]]:
    """
    Authenticate user.
    Returns (success, message, jwt_token).
    """
    db = get_db()
    user = db.users.find_one({"username": username})
    if not user:
        return False, "Invalid username or password.", None
    if not verify_password(password, user["password_hash"]):
        return False, "Invalid username or password.", None
    token = create_token(str(user["_id"]), username)
    return True, "Login successful!", token


def get_current_user() -> Optional[dict]:
    """Return current user info from Streamlit session state."""
    token = st.session_state.get("auth_token")
    if not token:
        return None
    payload = decode_token(token)
    if not payload:
        st.session_state.pop("auth_token", None)
        return None
    return payload


def logout() -> None:
    """Clear session state."""
    for key in ["auth_token", "username", "user_id"]:
        st.session_state.pop(key, None)


def require_auth() -> dict:
    """
    Ensure user is authenticated. If not, stop the page.
    Returns the payload dict if authenticated.
    """
    user = get_current_user()
    if not user:
        st.error("🔒 Please log in to access this page.")
        st.stop()
    return user


# ── Profile CRUD ──────────────────────────────────────────────────────────────

def get_profile(user_id: str) -> dict:
    db = get_db()
    profile = db.profiles.find_one({"user_id": user_id})
    if not profile:
        # Create empty profile lazily
        profile = UserProfile(user_id=user_id).to_dict()
        db.profiles.insert_one(profile)
    profile.pop("_id", None)
    return profile


def save_profile(user_id: str, data: dict) -> bool:
    db = get_db()
    data["user_id"] = user_id
    data["updated_at"] = datetime.utcnow()
    result = db.profiles.update_one(
        {"user_id": user_id},
        {"$set": data},
        upsert=True,
    )
    return result.acknowledged
